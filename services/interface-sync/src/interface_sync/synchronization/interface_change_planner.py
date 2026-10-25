from datetime import datetime

from interface_sync.constants.constants import (
    FIELD_CAPACITY_GBPS,
    FIELD_LAYER,
    FIELD_NAME,
    FIELD_VENDOR,
    UNDEFINED_VENDOR,
)
from interface_sync.constants.enums import InterfaceStatus
from interface_sync.exceptions import EmptyListingError, MissingLayerError
from interface_sync.models import PageConfig, ScrapedInterface, ValidatedListing
from interface_sync.persistence import InterfaceChanges, InterfaceDocument, InterfaceModification


class InterfaceChangePlanner:
    """Decides what must be written, comparing a scraped listing with the stored interfaces.

    It is pure: it neither reads nor writes the database. The repository applies its result.
    """

    def plan_page(
        self,
        page: PageConfig,
        listing: ValidatedListing,
        stored_interfaces: list[InterfaceDocument],
        now: datetime,
    ) -> InterfaceChanges:
        """Plan the registrations, updates and reactivations of one page [RF-007, RF-008, RF-009].

        Every complete interface is registered when its `scan_url` is not stored; otherwise it is
        compared with the stored one. An interface without differences produces no change, so
        its `updated_at` stays intact. Data and status changes of one interface are one
        modification. A `scan_url` repeated in the listing is planned only once.
        """
        stored_by_scan_url = {stored.scan_url: stored for stored in stored_interfaces}
        planned_scan_urls: set[str] = set()
        registrations: list[InterfaceDocument] = []
        modifications: list[InterfaceModification] = []
        unchanged_count = 0

        for interface in listing.complete_interfaces:
            scan_url = str(interface.scan_url)
            if scan_url in planned_scan_urls:
                continue
            planned_scan_urls.add(scan_url)

            stored = stored_by_scan_url.get(scan_url)
            if stored is None:
                registrations.append(self._build_registration(page, interface, now))
                continue
            modification = self._compare(page, interface, stored, now)
            if modification is None:
                unchanged_count += 1
            else:
                modifications.append(modification)

        return InterfaceChanges(
            registrations=registrations,
            modifications=modifications,
            unchanged_count=unchanged_count,
        )

    def plan_decommission(
        self,
        active_interfaces: list[InterfaceDocument],
        present_scan_urls: frozenset[str],
        now: datetime,
    ) -> InterfaceChanges:
        """Plan the decommission of the active interfaces missing from the listing [RF-009].

        An interface is present when its `scan_url` is in `present_scan_urls`, even if it was
        incomplete. Raise `EmptyListingError` when nothing is present: an empty listing must
        never decommission anything.
        """
        if not present_scan_urls:
            raise EmptyListingError("un listado vacío no puede desincorporar interfaces")
        modifications = [
            InterfaceModification(
                scan_url=active.scan_url,
                updated_at=now,
                status_change=(InterfaceStatus.ACTIVE, InterfaceStatus.DECOMMISSIONED),
            )
            for active in active_interfaces
            if active.scan_url not in present_scan_urls
        ]
        return InterfaceChanges(
            modifications=modifications,
            unchanged_count=len(active_interfaces) - len(modifications),
        )

    def _build_registration(
        self, page: PageConfig, interface: ScrapedInterface, now: datetime
    ) -> InterfaceDocument:
        """Build the document of an interface that is not stored yet."""
        return InterfaceDocument(
            layer=self._require_layer(interface),
            name=str(interface.name),
            vendor=self._obtain_vendor(page, interface),
            capacity_gbps=float(interface.capacity_gbps or 0.0),
            scan_url=str(interface.scan_url),
            status=InterfaceStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )

    def _compare(
        self,
        page: PageConfig,
        interface: ScrapedInterface,
        stored: InterfaceDocument,
        now: datetime,
    ) -> InterfaceModification | None:
        """Return the modification of a stored interface, or `None` when nothing changes."""
        obtained_values: dict[str, str | float] = {
            FIELD_NAME: str(interface.name),
            FIELD_LAYER: self._require_layer(interface),
            FIELD_CAPACITY_GBPS: self._resolve_capacity(interface, stored),
            FIELD_VENDOR: self._resolve_vendor(page, interface, stored),
        }
        field_changes = {
            field: (getattr(stored, field), value)
            for field, value in obtained_values.items()
            if getattr(stored, field) != value
        }
        status_change = (
            (InterfaceStatus.DECOMMISSIONED, InterfaceStatus.ACTIVE)
            if stored.status is InterfaceStatus.DECOMMISSIONED
            else None
        )
        if not field_changes and status_change is None:
            return None
        return InterfaceModification(
            scan_url=stored.scan_url,
            updated_at=now,
            field_changes=field_changes,
            status_change=status_change,
        )

    @staticmethod
    def _require_layer(interface: ScrapedInterface) -> str:
        """Return the layer of the interface; raise `MissingLayerError` if it has none."""
        if not interface.layer:
            raise MissingLayerError(f"La interfaz {interface.scan_url} no tiene capa")
        return interface.layer

    @staticmethod
    def _resolve_capacity(interface: ScrapedInterface, stored: InterfaceDocument) -> float:
        """Return the capacity to keep: a defaulted `0` never replaces a stored non-zero one."""
        obtained = float(interface.capacity_gbps or 0.0)
        if obtained == 0.0 and stored.capacity_gbps != 0.0:
            return stored.capacity_gbps
        return obtained

    def _resolve_vendor(
        self, page: PageConfig, interface: ScrapedInterface, stored: InterfaceDocument
    ) -> str:
        """Return the vendor to keep: any vendor other than `UNDEFINED` has priority."""
        obtained = self._obtain_vendor(page, interface)
        return stored.vendor if obtained == UNDEFINED_VENDOR else obtained

    def _obtain_vendor(self, page: PageConfig, interface: ScrapedInterface) -> str:
        """Return the vendor of the interface: the scraped one, else the page's, else undefined."""
        scraped_vendor = self._standardize_vendor(interface.vendor)
        if scraped_vendor != UNDEFINED_VENDOR:
            return scraped_vendor
        return self._standardize_vendor(page.vendor)

    @staticmethod
    def _standardize_vendor(vendor: str | None) -> str:
        """Strip and uppercase a vendor; a missing or empty one is `UNDEFINED`."""
        return (vendor or "").strip().upper() or UNDEFINED_VENDOR
