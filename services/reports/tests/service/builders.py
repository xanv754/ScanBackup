from bson import ObjectId

from reports.domain.models import AggregatedSummary, InterfaceInfo

GBPS = 1_000_000_000


def make_interface(
    name: str = "eth-1", vendor: str = "huawei", capacity: float = 10
) -> InterfaceInfo:
    """Build an interface with a new id."""
    return InterfaceInfo(
        id=ObjectId(), name=name, vendor=vendor, capacity_gbps=capacity, scan_url=f"url/{name}"
    )


def make_summary(
    interface: InterfaceInfo, days: int = 3, in_max_gbps: float = 5
) -> AggregatedSummary:
    """Build an aggregated summary for `interface`."""
    return AggregatedSummary(
        interface_id=interface.id,
        in_average_bps=1 * GBPS,
        out_average_bps=1 * GBPS,
        in_max_bps=in_max_gbps * GBPS,
        out_max_bps=1 * GBPS,
        days=days,
    )
