from interface_sync.exceptions import InvalidListingError
from interface_sync.models import PageConfig, ScrapedInterface, ValidatedListing
from interface_sync.utils.logger import ServiceLogger
from interface_sync.validation.capacity_validator import CapacityValidator
from interface_sync.validation.completeness_validator import (
    CompletenessValidator,
    IncompleteInterface,
)


class ListingValidator:
    """Validates the listing of a page and reports the warnings [RF-004, RF-005, RF-006].

    It is the only validation class that writes to the log. The final result of the page
    (successful or failed) is reported by the caller.
    """

    def __init__(
        self,
        completeness_validator: CompletenessValidator,
        capacity_validator: CapacityValidator,
        logger: ServiceLogger,
    ) -> None:
        """Receive the validators and the logger used to report warnings."""
        self._completeness_validator = completeness_validator
        self._capacity_validator = capacity_validator
        self._logger = logger

    def validate(self, page: PageConfig, interfaces: list[ScrapedInterface]) -> ValidatedListing:
        """Validate the interfaces scraped from a page.

        Incomplete interfaces are discarded before the capacity is checked. Raises
        `InvalidListingError` when the page has no interfaces or none of them is complete.
        """
        page_label = f"{page.layer} {page.vendor}"
        completeness = self._completeness_validator.split(interfaces)

        for incomplete in completeness.incomplete:
            self._report_incomplete(page_label, incomplete)

        if not interfaces:
            raise InvalidListingError("sin interfaces")
        if not completeness.complete:
            raise InvalidListingError("todas las interfaces están incompletas")

        capacity = self._capacity_validator.normalize(completeness.complete)

        for defaulted in capacity.defaulted:
            self._logger.warning(
                "Capacidad por defecto",
                f"{page_label} | posición {defaulted.position} | {defaulted.name}",
            )

        present_scan_urls = frozenset(
            interface.scan_url
            for interface in interfaces
            if interface.scan_url and interface.scan_url.strip()
        )

        return ValidatedListing(
            complete_interfaces=capacity.interfaces,
            present_scan_urls=present_scan_urls,
            incomplete_count=len(completeness.incomplete),
            defaulted_capacity_count=len(capacity.defaulted),
        )

    def _report_incomplete(self, page_label: str, incomplete: IncompleteInterface) -> None:
        """Log one warning with the page, the known data and the missing fields."""
        interface = incomplete.interface
        known_data = [
            f"{field_name}={value}"
            for field_name, value in (("nombre", interface.name), ("url", interface.scan_url))
            if value
        ]
        details = [page_label, f"posición {interface.position}", *known_data]
        details.append(f"faltan: {', '.join(incomplete.missing_fields)}")
        self._logger.warning("Interfaz incompleta", " | ".join(details))
