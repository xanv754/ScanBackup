import math

import pytest

from interface_sync.exceptions import InvalidListingError, PageFetchError
from interface_sync.models import PageConfig, ScrapedInterface
from interface_sync.utils.logger import ServiceLogger
from interface_sync.validation import CapacityValidator, CompletenessValidator, ListingValidator


class RecordingLogger(ServiceLogger):
    def __init__(self) -> None:
        self.records: list[tuple[str, str, str]] = []

    def info(self, message: str, details: str = "") -> None:
        self.records.append(("info", message, details))

    def warning(self, message: str, details: str = "") -> None:
        self.records.append(("warning", message, details))

    def error(self, message: str, details: str = "") -> None:
        self.records.append(("error", message, details))


def build_interface(
    position: int = 1,
    name: str | None = "IF-1",
    scan_url: str | None = "http://scan/1.log",
    capacity_gbps: float | None = 10.0,
) -> ScrapedInterface:
    return ScrapedInterface(
        position=position, name=name, scan_url=scan_url, capacity_gbps=capacity_gbps
    )


@pytest.fixture
def recording_logger() -> RecordingLogger:
    return RecordingLogger()


@pytest.fixture
def validator(recording_logger: RecordingLogger) -> ListingValidator:
    return ListingValidator(CompletenessValidator(), CapacityValidator(), recording_logger)


@pytest.fixture
def borde_page() -> PageConfig:
    return PageConfig(layer="borde", url="http://scan/borde", vendor="huawei")


@pytest.fixture
def bras_page() -> PageConfig:
    return PageConfig(layer="bras", url="http://scan/bras")


def test_valid_listing_continues_without_warnings(
    validator: ListingValidator, borde_page: PageConfig, recording_logger: RecordingLogger
):
    """RF-004/005/006: a fully complete listing with valid capacities passes silently."""
    interfaces = [
        build_interface(position=1, scan_url="http://scan/1.log"),
        build_interface(position=2, name="IF-2", scan_url="http://scan/2.log"),
    ]

    listing = validator.validate(borde_page, interfaces)

    assert listing.complete_interfaces == interfaces
    assert listing.present_scan_urls == {"http://scan/1.log", "http://scan/2.log"}
    assert listing.incomplete_count == 0
    assert listing.defaulted_capacity_count == 0
    assert recording_logger.records == []


def test_incomplete_interface_is_discarded_with_warning(
    validator: ListingValidator, borde_page: PageConfig, recording_logger: RecordingLogger
):
    """RF-004: an incomplete interface is warned once and does not fail the page."""
    complete = build_interface(position=1)
    incomplete = build_interface(position=2, name=None, scan_url="http://scan/2.log")

    listing = validator.validate(borde_page, [complete, incomplete])

    assert listing.complete_interfaces == [complete]
    assert listing.incomplete_count == 1
    assert recording_logger.records == [
        (
            "warning",
            "Interfaz incompleta",
            "BORDE HUAWEI | posición 2 | url=http://scan/2.log | faltan: name",
        )
    ]


def test_incomplete_warning_lists_known_data_and_all_missing_fields(
    validator: ListingValidator, borde_page: PageConfig, recording_logger: RecordingLogger
):
    """RF-004: the warning includes name and URL when they exist and every missing field."""
    complete = build_interface(position=1)
    without_url = build_interface(position=2, name="IF-2", scan_url=None)
    without_anything = build_interface(position=3, name=None, scan_url="")

    validator.validate(borde_page, [complete, without_url, without_anything])

    assert recording_logger.records == [
        (
            "warning",
            "Interfaz incompleta",
            "BORDE HUAWEI | posición 2 | nombre=IF-2 | faltan: scan_url",
        ),
        ("warning", "Interfaz incompleta", "BORDE HUAWEI | posición 3 | faltan: name, scan_url"),
    ]


def test_incomplete_interface_with_url_counts_as_present(
    validator: ListingValidator, borde_page: PageConfig
):
    """RF-004: an incomplete interface with scan_url is present but does not continue."""
    complete = build_interface(position=1, scan_url="http://scan/1.log")
    incomplete = build_interface(position=2, name="", scan_url="http://scan/2.log")
    without_url = build_interface(position=3, scan_url=None)

    listing = validator.validate(borde_page, [complete, incomplete, without_url])

    assert listing.present_scan_urls == {"http://scan/1.log", "http://scan/2.log"}
    assert [item.scan_url for item in listing.complete_interfaces] == ["http://scan/1.log"]


@pytest.mark.parametrize("capacity_gbps", [None, math.nan, math.inf, -1.0])
def test_invalid_capacity_defaults_to_zero_with_warning(
    validator: ListingValidator,
    borde_page: PageConfig,
    recording_logger: RecordingLogger,
    capacity_gbps: float | None,
):
    """RF-005: an invalid capacity becomes zero, is warned once and the interface continues."""
    interface = build_interface(position=3, name="IF-3", capacity_gbps=capacity_gbps)

    listing = validator.validate(borde_page, [interface])

    [continued] = listing.complete_interfaces
    assert continued.capacity_gbps == 0.0
    assert listing.defaulted_capacity_count == 1
    assert recording_logger.records == [
        ("warning", "Capacidad por defecto", "BORDE HUAWEI | posición 3 | IF-3")
    ]


def test_capacity_is_not_checked_on_incomplete_interfaces(
    validator: ListingValidator, borde_page: PageConfig, recording_logger: RecordingLogger
):
    """RF-005: incomplete interfaces are discarded first, so they get no capacity warning."""
    complete = build_interface(position=1)
    incomplete = build_interface(position=2, name=None, capacity_gbps=None)

    listing = validator.validate(borde_page, [complete, incomplete])

    assert listing.defaulted_capacity_count == 0
    assert [record[1] for record in recording_logger.records] == ["Interfaz incompleta"]


def test_listing_without_interfaces_is_invalid(
    validator: ListingValidator, borde_page: PageConfig, recording_logger: RecordingLogger
):
    """RF-006: a page with zero interfaces is an invalid listing and fails."""
    with pytest.raises(InvalidListingError) as error_info:
        validator.validate(borde_page, [])

    assert error_info.value.cause == "listado inválido (sin interfaces)"
    assert recording_logger.records == []


def test_listing_with_only_incomplete_interfaces_is_invalid(
    validator: ListingValidator, borde_page: PageConfig, recording_logger: RecordingLogger
):
    """RF-006: all interfaces incomplete is an invalid listing; each one is still warned."""
    interfaces = [
        build_interface(position=1, name=None),
        build_interface(position=2, scan_url=None),
    ]

    with pytest.raises(InvalidListingError) as error_info:
        validator.validate(borde_page, interfaces)

    assert error_info.value.cause == "listado inválido (todas las interfaces están incompletas)"
    assert [record[1] for record in recording_logger.records] == ["Interfaz incompleta"] * 2


def test_invalid_listing_is_a_page_failure(validator: ListingValidator, borde_page: PageConfig):
    """RF-006: the error is a PageFetchError so the caller handles it as any failed page."""
    with pytest.raises(PageFetchError):
        validator.validate(borde_page, [])


def test_bras_listing_uses_page_label_and_interface_vendors(
    validator: ListingValidator, bras_page: PageConfig, recording_logger: RecordingLogger
):
    """RF-004/005/006: Bras pages validate like any other; vendors stay on each interface."""
    uplink = ScrapedInterface(
        position=1, name="UP-1", scan_url="http://scan/u.log", capacity_gbps=10.0, vendor="Uplink"
    )
    downlink = ScrapedInterface(
        position=2,
        name="DOWN-1",
        scan_url="http://scan/d.log",
        capacity_gbps=None,
        vendor="Downlink",
    )
    broken = ScrapedInterface(
        position=3, name=None, scan_url=None, capacity_gbps=10.0, vendor="Downlink"
    )

    listing = validator.validate(bras_page, [uplink, downlink, broken])

    assert [item.vendor for item in listing.complete_interfaces] == ["Uplink", "Downlink"]
    assert [item.capacity_gbps for item in listing.complete_interfaces] == [10.0, 0.0]
    assert recording_logger.records == [
        ("warning", "Interfaz incompleta", "BRAS UNDEFINED | posición 3 | faltan: name, scan_url"),
        ("warning", "Capacidad por defecto", "BRAS UNDEFINED | posición 2 | DOWN-1"),
    ]
