import math

import pytest

from interface_sync.models import ScrapedInterface
from interface_sync.validation import CapacityValidator


def build_interface(capacity_gbps: float | None, position: int = 1) -> ScrapedInterface:
    return ScrapedInterface(
        position=position, name=f"IF-{position}", scan_url="http://scan/1.log",
        capacity_gbps=capacity_gbps,
    )


@pytest.fixture
def validator() -> CapacityValidator:
    return CapacityValidator()


@pytest.mark.parametrize("capacity_gbps", [0.0, 1.0, 10.0, 100.0, 0.5])
def test_valid_capacity_is_kept(validator: CapacityValidator, capacity_gbps: float):
    """RF-005: a numeric, finite and non-negative capacity (zero included) is not modified."""
    interface = build_interface(capacity_gbps)

    result = validator.normalize([interface])

    assert result.interfaces == [interface]
    assert result.defaulted == []


@pytest.mark.parametrize("capacity_gbps", [None, math.nan, math.inf, -math.inf, -1.0, -0.5])
def test_invalid_capacity_becomes_zero(validator: CapacityValidator, capacity_gbps: float | None):
    """RF-005: a missing, non-finite or negative capacity is replaced by zero."""
    interface = build_interface(capacity_gbps)

    result = validator.normalize([interface])

    [normalized] = result.interfaces
    assert normalized.capacity_gbps == 0.0
    assert isinstance(normalized.capacity_gbps, float)
    assert result.defaulted == [interface]


def test_normalization_keeps_the_rest_of_the_interface(validator: CapacityValidator):
    """RF-005: only the capacity changes; the received interface is not mutated."""
    interface = build_interface(None, position=4)

    [normalized] = validator.normalize([interface]).interfaces

    assert (normalized.position, normalized.name, normalized.scan_url) == (
        4, "IF-4", "http://scan/1.log",
    )
    assert interface.capacity_gbps is None


def test_mixed_listing_keeps_order_and_reports_only_defaulted(validator: CapacityValidator):
    """RF-005: valid and invalid capacities coexist; order is kept and one page does not fail."""
    valid = build_interface(10.0, position=1)
    invalid = build_interface(math.nan, position=2)
    other_valid = build_interface(100.0, position=3)

    result = validator.normalize([valid, invalid, other_valid])

    assert [item.position for item in result.interfaces] == [1, 2, 3]
    assert [item.capacity_gbps for item in result.interfaces] == [10.0, 0.0, 100.0]
    assert result.defaulted == [invalid]


def test_empty_listing_has_nothing_to_normalize(validator: CapacityValidator):
    """RF-005: an empty listing yields empty results."""
    result = validator.normalize([])

    assert result.interfaces == []
    assert result.defaulted == []
