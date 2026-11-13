from collections.abc import Callable
from datetime import datetime

import pytest

from interface_sync.constants.enums import InterfaceStatus
from interface_sync.exceptions import EmptyListingError, MissingLayerError
from interface_sync.models import PageConfig, ScrapedInterface, ValidatedListing
from interface_sync.persistence import InterfaceDocument
from interface_sync.synchronization import InterfaceChangePlanner

Scraped = Callable[..., ScrapedInterface]
Listing = Callable[..., ValidatedListing]
Document = Callable[..., InterfaceDocument]


@pytest.fixture
def planner() -> InterfaceChangePlanner:
    return InterfaceChangePlanner()


@pytest.fixture
def huawei_page() -> PageConfig:
    return PageConfig(layer="borde", url="http://scan/borde", vendor="huawei")


@pytest.fixture
def undefined_page() -> PageConfig:
    return PageConfig(layer="bras", url="http://scan/bras", vendor="undefined")


def test_new_interface_is_registered_as_active(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    now: datetime,
):
    """RF-007: an unknown scan_url is registered active with equal creation and update dates."""
    interface = make_scraped(capacity_gbps=40)

    changes = planner.plan_page(huawei_page, make_listing([interface]), [], now)

    assert changes.modifications == []
    [document] = changes.registrations
    assert document.id is None
    assert document.status is InterfaceStatus.ACTIVE
    assert document.created_at == document.updated_at == now
    assert (document.layer, document.name, document.vendor) == ("BORDE", "IF-1", "HUAWEI")
    assert document.scan_url == "http://scan/1.log"
    assert document.capacity_gbps == 40.0
    assert isinstance(document.capacity_gbps, float)


def test_registration_takes_vendor_from_page_when_scraping_gives_none(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    now: datetime,
):
    """RF-007: a vendor that could not be scraped falls back to the one of config.yml."""
    interface = make_scraped(vendor=None)

    changes = planner.plan_page(huawei_page, make_listing([interface]), [], now)

    assert changes.registrations[0].vendor == "HUAWEI"


@pytest.mark.parametrize("scraped_vendor", [None, "", "   ", "undefined", "UnDefined"])
def test_registration_without_any_vendor_is_undefined(
    planner: InterfaceChangePlanner,
    undefined_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    now: datetime,
    scraped_vendor: str | None,
):
    """RF-007: no vendor from the scraping nor from config.yml is stored as UNDEFINED."""
    interface = make_scraped(vendor=scraped_vendor, layer="BRAS")

    changes = planner.plan_page(undefined_page, make_listing([interface]), [], now)

    assert changes.registrations[0].vendor == "UNDEFINED"


def test_registration_standardizes_scraped_vendor(
    planner: InterfaceChangePlanner,
    undefined_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    now: datetime,
):
    """RF-007: the scraped vendor is stripped and stored in uppercase."""
    interface = make_scraped(vendor="  uplink ", layer="BRAS")

    changes = planner.plan_page(undefined_page, make_listing([interface]), [], now)

    assert changes.registrations[0].vendor == "UPLINK"


def test_identical_interface_produces_no_change(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
):
    """RF-008/RF-011: without differences nothing is written, so updated_at stays intact."""
    changes = planner.plan_page(huawei_page, make_listing([make_scraped()]), [make_document()], now)

    assert changes.registrations == []
    assert changes.modifications == []
    assert changes.unchanged_count == 1


@pytest.mark.parametrize(
    ("field", "obtained", "stored_value", "expected_change"),
    [
        ("name", "NEW NAME", "IF-1", ("IF-1", "NEW NAME")),
        ("layer", "DIST", "BORDE", ("BORDE", "DIST")),
        ("capacity_gbps", 100.0, 10.0, (10.0, 100.0)),
    ],
)
def test_single_changed_field_is_the_only_modification(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
    field: str,
    obtained: object,
    stored_value: object,
    expected_change: tuple[object, object],
):
    """RF-008: only the field that differs is modified, together with updated_at."""
    interface = make_scraped(**{field: obtained})
    stored = make_document(**{field: stored_value})

    changes = planner.plan_page(huawei_page, make_listing([interface]), [stored], now)

    [modification] = changes.modifications
    assert modification.field_changes == {field: expected_change}
    assert modification.status_change is None
    assert modification.updated_at == now
    assert changes.updated_count == 1


@pytest.mark.parametrize(
    ("obtained_vendor", "stored_vendor", "expected_vendor"),
    [
        ("UNDEFINED", "UPLINK", None),
        ("UNDEFINED", "UNDEFINED", None),
        ("UPLINK", "UNDEFINED", "UPLINK"),
        ("DOWNLINK", "UPLINK", "DOWNLINK"),
        ("UPLINK", "UPLINK", None),
    ],
    ids=[
        "undefined_keeps_stored_concrete",
        "undefined_keeps_stored_undefined",
        "concrete_replaces_stored_undefined",
        "concrete_replaces_other_concrete",
        "same_concrete_no_change",
    ],
)
def test_vendor_priority_rules(
    planner: InterfaceChangePlanner,
    undefined_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
    obtained_vendor: str,
    stored_vendor: str,
    expected_vendor: str | None,
):
    """RF-008: any vendor other than UNDEFINED has priority; UNDEFINED never replaces one."""
    interface = make_scraped(vendor=obtained_vendor, layer="BRAS")
    stored = make_document(vendor=stored_vendor, layer="BRAS")

    changes = planner.plan_page(undefined_page, make_listing([interface]), [stored], now)

    if expected_vendor is None:
        assert changes.modifications == []
        assert changes.unchanged_count == 1
    else:
        [modification] = changes.modifications
        assert modification.field_changes == {"vendor": (stored_vendor, expected_vendor)}


def test_unextracted_vendor_does_not_override_stored_concrete_vendor(
    planner: InterfaceChangePlanner,
    undefined_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
):
    """RF-008: no scraped vendor and UNDEFINED in config.yml keep the stored concrete vendor."""
    interface = make_scraped(vendor=None, name="OTHER NAME", layer="BRAS")
    stored = make_document(vendor="UPLINK", layer="BRAS")

    changes = planner.plan_page(undefined_page, make_listing([interface]), [stored], now)

    [modification] = changes.modifications
    assert modification.field_changes == {"name": ("IF-1", "OTHER NAME")}


def test_defaulted_zero_capacity_does_not_replace_stored_capacity(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
):
    """RF-008: an obtained capacity of 0 never replaces a stored non-zero capacity."""
    interface = make_scraped(capacity_gbps=0.0)
    stored = make_document(capacity_gbps=25.0)

    changes = planner.plan_page(huawei_page, make_listing([interface]), [stored], now)

    assert changes.modifications == []
    assert changes.unchanged_count == 1


def test_numeric_capacity_replaces_stored_zero(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
):
    """RF-008: a stored 0 (unknown capacity) is replaced by a numeric obtained one."""
    interface = make_scraped(capacity_gbps=10.0)
    stored = make_document(capacity_gbps=0.0)

    changes = planner.plan_page(huawei_page, make_listing([interface]), [stored], now)

    [modification] = changes.modifications
    assert modification.field_changes == {"capacity_gbps": (0.0, 10.0)}


def test_zero_capacity_over_zero_capacity_is_not_a_change(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
):
    """RF-008/RF-011: 0 against 0 leaves the record untouched."""
    changes = planner.plan_page(
        huawei_page,
        make_listing([make_scraped(capacity_gbps=0.0)]),
        [make_document(capacity_gbps=0.0)],
        now,
    )

    assert changes.modifications == []


def test_missing_capacity_is_treated_as_zero(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    now: datetime,
):
    """RF-007: a capacity that was left undefined is registered as 0.0."""
    changes = planner.plan_page(
        huawei_page, make_listing([make_scraped(capacity_gbps=None)]), [], now
    )

    assert changes.registrations[0].capacity_gbps == 0.0


def test_reappearing_decommissioned_interface_is_reactivated(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
):
    """RF-009: a decommissioned interface that is listed again becomes active."""
    stored = make_document(status=InterfaceStatus.DECOMMISSIONED)

    changes = planner.plan_page(huawei_page, make_listing([make_scraped()]), [stored], now)

    [modification] = changes.modifications
    assert modification.status_change == (InterfaceStatus.DECOMMISSIONED, InterfaceStatus.ACTIVE)
    assert modification.field_changes == {}
    assert changes.reactivated_count == 1
    assert changes.updated_count == 0


def test_reactivation_with_data_changes_is_a_single_modification(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
):
    """RF-008/RF-009: data and status of one interface are applied together, with one date."""
    interface = make_scraped(name="RENAMED", capacity_gbps=100.0)
    stored = make_document(status=InterfaceStatus.DECOMMISSIONED)

    changes = planner.plan_page(huawei_page, make_listing([interface]), [stored], now)

    [modification] = changes.modifications
    assert modification.status_change == (InterfaceStatus.DECOMMISSIONED, InterfaceStatus.ACTIVE)
    assert set(modification.field_changes) == {"name", "capacity_gbps"}
    assert modification.updated_at == now
    assert changes.reactivated_count == 1
    assert changes.updated_count == 1


def test_active_interface_is_never_given_a_status_change_by_the_page_plan(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
):
    """RF-009: listing an already active interface does not touch its status."""
    changes = planner.plan_page(
        huawei_page,
        make_listing([make_scraped(name="RENAMED")]),
        [make_document()],
        now,
    )

    assert changes.modifications[0].status_change is None


def test_page_plan_mixes_registrations_updates_and_unchanged(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
):
    """RF-007/RF-008: one page can register, update and leave interfaces alone at once."""
    interfaces = [
        make_scraped(position=1, scan_url="http://scan/new.log"),
        make_scraped(position=2, scan_url="http://scan/changed.log", name="NEW"),
        make_scraped(position=3, scan_url="http://scan/same.log"),
    ]
    stored = [
        make_document(scan_url="http://scan/changed.log", name="OLD"),
        make_document(scan_url="http://scan/same.log"),
    ]

    changes = planner.plan_page(huawei_page, make_listing(interfaces), stored, now)

    assert [document.scan_url for document in changes.registrations] == ["http://scan/new.log"]
    assert [modification.scan_url for modification in changes.modifications] == [
        "http://scan/changed.log"
    ]
    assert changes.unchanged_count == 1


def test_repeated_scan_url_in_a_listing_is_planned_once(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    now: datetime,
):
    """RF-007: the same scan_url twice in one listing is never registered twice."""
    interfaces = [make_scraped(position=1), make_scraped(position=2, name="DUPLICATE")]

    changes = planner.plan_page(huawei_page, make_listing(interfaces), [], now)

    assert len(changes.registrations) == 1
    assert changes.registrations[0].name == "IF-1"


def test_interface_without_layer_is_rejected_on_registration(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    now: datetime,
):
    """RF-007: the layer is mandatory; a missing one is a programming error, not a default."""
    with pytest.raises(MissingLayerError):
        planner.plan_page(huawei_page, make_listing([make_scraped(layer=None)]), [], now)


def test_interface_without_layer_is_rejected_on_update(
    planner: InterfaceChangePlanner,
    huawei_page: PageConfig,
    make_scraped: Scraped,
    make_listing: Listing,
    make_document: Document,
    now: datetime,
):
    """RF-008: the layer is mandatory when comparing with a stored interface too."""
    with pytest.raises(MissingLayerError):
        planner.plan_page(
            huawei_page, make_listing([make_scraped(layer="")]), [make_document()], now
        )


def test_missing_active_interface_is_decommissioned(
    planner: InterfaceChangePlanner, make_document: Document, now: datetime
):
    """RF-009: an active interface absent from the listing becomes decommissioned."""
    active = [make_document(scan_url="http://scan/gone.log")]

    changes = planner.plan_decommission(active, frozenset({"http://scan/other.log"}), now)

    [modification] = changes.modifications
    assert modification.scan_url == "http://scan/gone.log"
    assert modification.status_change == (InterfaceStatus.ACTIVE, InterfaceStatus.DECOMMISSIONED)
    assert modification.field_changes == {}
    assert modification.updated_at == now
    assert changes.decommissioned_count == 1


def test_present_active_interface_is_not_decommissioned(
    planner: InterfaceChangePlanner, make_document: Document, now: datetime
):
    """RF-009: an interface whose scan_url is present (even if incomplete) is kept."""
    active = [make_document(scan_url="http://scan/incomplete.log")]

    changes = planner.plan_decommission(active, frozenset({"http://scan/incomplete.log"}), now)

    assert changes.modifications == []
    assert changes.unchanged_count == 1


def test_decommission_only_affects_missing_interfaces(
    planner: InterfaceChangePlanner, make_document: Document, now: datetime
):
    """RF-009: with present and missing interfaces, only the missing ones change."""
    active = [
        make_document(scan_url="http://scan/a.log"),
        make_document(scan_url="http://scan/b.log"),
        make_document(scan_url="http://scan/c.log"),
    ]

    changes = planner.plan_decommission(active, frozenset({"http://scan/b.log"}), now)

    assert [modification.scan_url for modification in changes.modifications] == [
        "http://scan/a.log",
        "http://scan/c.log",
    ]
    assert changes.unchanged_count == 1


def test_decommission_without_active_interfaces_is_empty(
    planner: InterfaceChangePlanner, now: datetime
):
    """RF-009: a layer with nothing active has nothing to decommission."""
    changes = planner.plan_decommission([], frozenset({"http://scan/a.log"}), now)

    assert changes.modifications == []
    assert changes.unchanged_count == 0


def test_empty_listing_never_decommissions(
    planner: InterfaceChangePlanner, make_document: Document, now: datetime
):
    """RF-006/RF-009: an empty set of present scan_urls is refused instead of emptying the layer."""
    with pytest.raises(EmptyListingError):
        planner.plan_decommission([make_document()], frozenset(), now)
