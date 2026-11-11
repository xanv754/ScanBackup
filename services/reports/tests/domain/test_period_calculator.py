import pytest
from bson import ObjectId

from reports.domain.models import AggregatedSummary, InterfaceInfo
from reports.domain.period_calculator import PeriodCalculator

GBPS = 1_000_000_000


def interface(
    capacity_gbps: float = 10, vendor: str = "huawei", name: str = "eth-1"
) -> InterfaceInfo:
    """Build an interface with the given values."""
    return InterfaceInfo(
        id=ObjectId(), name=name, vendor=vendor, capacity_gbps=capacity_gbps, scan_url="url"
    )


def summary(
    in_average: float = 0, out_average: float = 0, in_max: float = 0, out_max: float = 0
) -> AggregatedSummary:
    """Build an aggregated summary from bps values."""
    return AggregatedSummary(
        interface_id=ObjectId(),
        in_average_bps=in_average,
        out_average_bps=out_average,
        in_max_bps=in_max,
        out_max_bps=out_max,
        days=3,
    )


def test_rf035_rf037_values_are_converted_to_gbps() -> None:
    """RF-035, RF-037: the four values are divided by 1e9 without rounding."""
    row = PeriodCalculator().calculate(interface(), summary(4 * GBPS, 1 * GBPS, 9 * GBPS, 3 * GBPS))
    assert (row.in_average_gbps, row.out_average_gbps) == (4.0, 1.0)
    assert (row.in_max_gbps, row.out_max_gbps) == (9.0, 3.0)


def test_rf038_usage_uses_the_greater_maximum() -> None:
    """RF-038: with capacity 10, in_max 9 and out_max 3 the usage is 90."""
    row = PeriodCalculator().calculate(
        interface(capacity_gbps=10), summary(4 * GBPS, 1 * GBPS, 9 * GBPS, 3 * GBPS)
    )
    assert row.usage_percent == pytest.approx(90.0)


def test_rf038_usage_can_use_the_out_maximum() -> None:
    """RF-038: usage uses out_max when it is the greater one."""
    row = PeriodCalculator().calculate(
        interface(capacity_gbps=10), summary(in_max=2 * GBPS, out_max=5 * GBPS)
    )
    assert row.usage_percent == pytest.approx(50.0)


def test_rf038_capacity_zero_gives_zero_usage() -> None:
    """RF-038: capacity 0 gives usage 0 and the capacity is kept as 0."""
    row = PeriodCalculator().calculate(interface(capacity_gbps=0), summary(in_max=5 * GBPS))
    assert row.usage_percent == 0
    assert row.capacity_gbps == 0


def test_rf038_usage_has_no_upper_limit() -> None:
    """RF-038: usage above 100 is kept."""
    row = PeriodCalculator().calculate(interface(capacity_gbps=2), summary(in_max=5 * GBPS))
    assert row.usage_percent == pytest.approx(250.0)


def test_rf035_zero_values_are_valid() -> None:
    """RF-035: a traffic value of 0 is included in the result as 0."""
    row = PeriodCalculator().calculate(interface(), summary())
    assert (row.in_average_gbps, row.in_max_gbps, row.out_average_gbps, row.out_max_gbps) == (
        0,
        0,
        0,
        0,
    )
    assert row.usage_percent == 0


def test_rf040_name_and_vendor_are_uppercase() -> None:
    """RF-040: interface and type are exported in uppercase."""
    row = PeriodCalculator().calculate(interface(vendor=" Huawei ", name="Eth-1/0"), summary())
    assert (row.name, row.vendor) == ("ETH-1/0", "HUAWEI")


@pytest.mark.parametrize("vendor", ["", "   "])
def test_rf040_empty_vendor_is_undefined(vendor: str) -> None:
    """RF-040: an empty vendor is exported as UNDEFINED."""
    assert PeriodCalculator().calculate(interface(vendor=vendor), summary()).vendor == "UNDEFINED"


def test_rf040_rows_sort_by_type_then_name_then_scan_url() -> None:
    """RF-040: the order key is (type, interface) with the SCAN URL as tie breaker."""
    calculator = PeriodCalculator()
    first = calculator.calculate(interface(vendor="a", name="z"), summary())
    second = calculator.calculate(interface(vendor="b", name="a"), summary())
    assert first.sort_key < second.sort_key
