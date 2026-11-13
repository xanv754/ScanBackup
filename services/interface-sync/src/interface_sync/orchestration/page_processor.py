from datetime import UTC, datetime

from interface_sync.constants.enums import LogEvent
from interface_sync.exceptions import DatabaseError, PageFetchError
from interface_sync.models import PageConfig, PageResult
from interface_sync.persistence import InterfaceRepository
from interface_sync.scraping import PageScraper
from interface_sync.synchronization import ChangeReporter, InterfaceChangePlanner, ScanUrlClaims
from interface_sync.utils.logger import ServiceLogger
from interface_sync.validation import ListingValidator


class PageProcessor:
    """Runs the full flow of one page: scraping, validation and storage [RF-007, RF-008, RF-010].

    It registers, updates and reactivates interfaces. Decommissioning needs every page of a
    layer, so it is done later by `LayerDecommissioner`. A `PageFetchError` or a `DatabaseError`
    never propagates: it becomes a failed `PageResult`, so the caller can keep processing the
    remaining pages. A page that fails before storage never touches the database. The instance
    lives for one run: it keeps the `scan_url` already taken by earlier pages.
    """

    def __init__(
        self,
        scraper: PageScraper,
        listing_validator: ListingValidator,
        repository: InterfaceRepository,
        planner: InterfaceChangePlanner,
        change_reporter: ChangeReporter,
        scan_url_claims: ScanUrlClaims,
        logger: ServiceLogger,
    ) -> None:
        """Receive the collaborators of the page flow and the logger of the page results."""
        self._scraper = scraper
        self._listing_validator = listing_validator
        self._repository = repository
        self._planner = planner
        self._change_reporter = change_reporter
        self._scan_url_claims = scan_url_claims
        self._logger = logger

    def process(self, page: PageConfig) -> PageResult:
        """Process the page and return its result; the outcome is also written to the log."""
        page_label = page.label
        try:
            interfaces = self._scraper.scrape(page)
            listing = self._listing_validator.validate(page, interfaces)
        except PageFetchError as error:
            self._logger.error(LogEvent.PAGE_FAILED, f"{page_label} | {error.cause}")
            return PageResult(page_label=page_label, layer=page.layer, cause=error.cause)

        listing, duplicated_scan_urls = self._scan_url_claims.claim(listing)
        for scan_url in duplicated_scan_urls:
            self._logger.warning(LogEvent.DUPLICATED_INTERFACE, f"{page_label} | {scan_url}")

        try:
            stored_interfaces = self._repository.find_by_scan_urls(
                {str(interface.scan_url) for interface in listing.complete_interfaces}
            )
            changes = self._planner.plan_page(page, listing, stored_interfaces, datetime.now(UTC))
            self._repository.apply(changes)
        except DatabaseError as error:
            self._logger.error(LogEvent.DATABASE_FAILED, f"{page_label} | {error.cause}")
            return PageResult(page_label=page_label, layer=page.layer, database_cause=error.cause)

        self._change_reporter.report(changes)
        self._logger.info(
            LogEvent.PAGE_SUMMARY,
            f"{page_label} | nuevas: {len(changes.registrations)} | "
            f"actualizadas: {changes.updated_count} | "
            f"reactivadas: {changes.reactivated_count} | "
            f"sin cambios: {changes.unchanged_count} | "
            f"incompletas: {listing.incomplete_count} | "
            f"duplicadas: {len(duplicated_scan_urls)} | "
            f"capacidad por defecto: {listing.defaulted_capacity_count}",
        )
        self._logger.info(LogEvent.PAGE_SUCCEEDED, page_label)
        return PageResult(
            page_label=page_label,
            layer=page.layer,
            present_scan_urls=listing.present_scan_urls,
        )
