from interface_sync.exceptions import PageFetchError
from interface_sync.models import PageConfig, PageResult
from interface_sync.scraping import PageScraper
from interface_sync.utils.logger import ServiceLogger
from interface_sync.validation import ListingValidator


class PageProcessor:
    """Runs the full flow of one page: scraping, validation and (pending) storage [RF-010].

    A `PageFetchError` never propagates: it becomes a failed `PageResult`, so the caller
    can keep processing the remaining pages.
    """

    def __init__(
        self,
        scraper: PageScraper,
        listing_validator: ListingValidator,
        logger: ServiceLogger,
    ) -> None:
        """Receive the scraper, the listing validator and the logger of the page results."""
        self._scraper = scraper
        self._listing_validator = listing_validator
        self._logger = logger

    def process(self, page: PageConfig) -> PageResult:
        """Process the page and return its result; the outcome is also written to the log."""
        page_label = page.label
        try:
            interfaces = self._scraper.scrape(page)
            listing = self._listing_validator.validate(page, interfaces)
        except PageFetchError as error:
            self._logger.error("Página fallida", f"{page_label} | {error.cause}")
            return PageResult(page_label=page_label, cause=error.cause)

        # TODO: persist `listing` (register, update and change status) with the interface
        # repository, log the page summary and turn a database error into a failed page.
        self._logger.info(
            "Página exitosa",
            f"{page_label} | {len(listing.complete_interfaces)} interfaces completas | "
            f"{listing.incomplete_count} incompletas | "
            f"{listing.defaulted_capacity_count} con capacidad por defecto",
        )
        return PageResult(page_label=page_label)
