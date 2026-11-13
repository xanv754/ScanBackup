from statistics import fmean

from traffic_collector.constants.constants import SCAN_VALUE_TO_BPS_FACTOR
from traffic_collector.domain import DailySummary, DailyTraffic


class DailySummaryCalculator:
    """Calculates the daily summary of an interface. Pure: no network, no database."""

    def calculate(self, daily_traffic: DailyTraffic) -> DailySummary | None:
        """Return the summary of the day, or None when it has no samples.

        `in_avg` and `out_avg` are the mean of the sample averages; `in_max` and `out_max` are
        the maximum of the sample maximums (maximums are never averaged). SCAN values are
        multiplied by `SCAN_VALUE_TO_BPS_FACTOR` (8.022, the legacy 0.000000008022 factor
        expressed in bps instead of Gbps).
        """
        samples = daily_traffic.samples
        if not samples:
            return None
        return DailySummary(
            interface_id=daily_traffic.interface_id,
            date=daily_traffic.date,
            in_avg=fmean(sample.in_avg for sample in samples)
            * SCAN_VALUE_TO_BPS_FACTOR,
            out_avg=fmean(sample.out_avg for sample in samples)
            * SCAN_VALUE_TO_BPS_FACTOR,
            in_max=max(sample.in_max for sample in samples) * SCAN_VALUE_TO_BPS_FACTOR,
            out_max=max(sample.out_max for sample in samples)
            * SCAN_VALUE_TO_BPS_FACTOR,
        )
