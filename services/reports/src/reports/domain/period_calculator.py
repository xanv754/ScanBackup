from reports.constants.constants import BPS_PER_GBPS, PERCENT_FACTOR, UNDEFINED_VENDOR
from reports.domain.models import AggregatedSummary, InterfaceInfo, InterfaceRow


class PeriodCalculator:
    """Turns the aggregated summaries of an interface into the values of the report.

    The database already computed the average of the daily averages and the maximum of the
    daily maximums, in bps. Usage is `max(in_max, out_max) / capacity * 100` with both values
    in Gbps and no upper limit; it is 0 when the capacity is 0 [RF-038]. Nothing is rounded.
    """

    def calculate(self, interface: InterfaceInfo, summary: AggregatedSummary) -> InterfaceRow:
        """Return the report row of `interface` [RF-035 to RF-038]."""
        in_max_gbps = summary.in_max_bps / BPS_PER_GBPS
        out_max_gbps = summary.out_max_bps / BPS_PER_GBPS
        return InterfaceRow(
            name=interface.name.upper(),
            in_average_gbps=summary.in_average_bps / BPS_PER_GBPS,
            in_max_gbps=in_max_gbps,
            out_average_gbps=summary.out_average_bps / BPS_PER_GBPS,
            out_max_gbps=out_max_gbps,
            capacity_gbps=interface.capacity_gbps,
            vendor=interface.vendor.strip().upper() or UNDEFINED_VENDOR,
            usage_percent=self._usage_percent(
                max(in_max_gbps, out_max_gbps), interface.capacity_gbps
            ),
            scan_url=interface.scan_url,
        )

    @staticmethod
    def _usage_percent(max_traffic_gbps: float, capacity_gbps: float) -> float:
        """Return the usage in percent, or 0 when the capacity is 0."""
        if capacity_gbps == 0:
            return 0.0
        return max_traffic_gbps / capacity_gbps * PERCENT_FACTOR
