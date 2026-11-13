import pytest

from interface_sync.models import ScrapedInterface
from interface_sync.validation import CompletenessValidator


def build_interface(
    position: int = 1, name: str | None = "IF-1", scan_url: str | None = "http://scan/1.log"
) -> ScrapedInterface:
    return ScrapedInterface(position=position, name=name, scan_url=scan_url, capacity_gbps=10.0)


@pytest.fixture
def validator() -> CompletenessValidator:
    return CompletenessValidator()


def test_complete_interface_passes(validator: CompletenessValidator):
    """RF-004: an interface with name and scan_url is complete."""
    interface = build_interface()

    result = validator.split([interface])

    assert result.complete == [interface]
    assert result.incomplete == []


@pytest.mark.parametrize(
    ("name", "scan_url", "missing_fields"),
    [
        (None, "http://scan/1.log", ["name"]),
        ("", "http://scan/1.log", ["name"]),
        ("   ", "http://scan/1.log", ["name"]),
        ("IF-1", None, ["scan_url"]),
        ("IF-1", "", ["scan_url"]),
        ("IF-1", "  ", ["scan_url"]),
        (None, None, ["name", "scan_url"]),
        ("", " ", ["name", "scan_url"]),
    ],
)
def test_interface_with_missing_data_is_incomplete(
    validator: CompletenessValidator,
    name: str | None,
    scan_url: str | None,
    missing_fields: list[str],
):
    """RF-004: absent, empty or blank name or scan_url makes the interface incomplete."""
    interface = build_interface(name=name, scan_url=scan_url)

    result = validator.split([interface])

    assert result.complete == []
    [incomplete] = result.incomplete
    assert incomplete.interface == interface
    assert incomplete.missing_fields == missing_fields


def test_mixed_listing_is_split_keeping_order(validator: CompletenessValidator):
    """RF-004: complete and incomplete interfaces are separated, each in listing order."""
    first = build_interface(position=1)
    broken = build_interface(position=2, name=None)
    last = build_interface(position=3, scan_url="http://scan/3.log")

    result = validator.split([first, broken, last])

    assert result.complete == [first, last]
    assert [item.interface for item in result.incomplete] == [broken]


def test_empty_listing_has_nothing_to_split(validator: CompletenessValidator):
    """RF-004: an empty listing yields no complete and no incomplete interfaces."""
    result = validator.split([])

    assert result.complete == []
    assert result.incomplete == []
