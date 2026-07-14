from collections import defaultdict
from datetime import date
from statistics import mean
from scanbackup.domain.entities.bbip.traffic.source import TrafficSourceBBIPEntity
from scanbackup.domain.entities.bbip.traffic.summaries.daily import (
    TrafficDailySummaryBBIPEntity,
)
from scanbackup.domain.entities.bbip.traffic.reports.daily import (
    TrafficDailyReportBBIPEntity,
)
from scanbackup.shared import PyObjectId


class TrafficReportService:
    """Builds traffic report rows from sources and summaries, and rolls up daily summaries into monthly aggregates."""

    @staticmethod
    def build_rows(
        sources: list[TrafficSourceBBIPEntity],
        summaries: list[TrafficDailySummaryBBIPEntity],
    ) -> list[TrafficDailyReportBBIPEntity]:
        """Join every summary with its active source, dropping summaries with no matching active source."""
        sources_by_id: dict[PyObjectId, TrafficSourceBBIPEntity] = {
            source.id: source for source in sources
        }

        rows = []
        for summary in summaries:
            source = sources_by_id.get(summary.device)
            if not source:
                continue
            rows.append(
                TrafficDailyReportBBIPEntity(
                    interface=source.interface,
                    model=source.model,
                    capacity=source.capacity,
                    layer=source.layer,
                    date=summary.date,
                    in_prom=summary.in_prom,
                    in_max=summary.in_max,
                    out_prom=summary.out_prom,
                    out_max=summary.out_max,
                    use=summary.use,
                )
            )
        return rows

    @staticmethod
    def aggregate_monthly(
        summaries: list[TrafficDailySummaryBBIPEntity], month_start: date
    ) -> list[TrafficDailySummaryBBIPEntity]:
        """Reduce every device's daily summaries within a month into a single monthly rollup per device.

        The "prom" values are averaged, while the "max" and "use" values keep
        the highest value recorded during the month.
        """
        grouped: dict[PyObjectId, list[TrafficDailySummaryBBIPEntity]] = defaultdict(
            list
        )
        for summary in summaries:
            grouped[summary.device].append(summary)

        return [
            TrafficDailySummaryBBIPEntity(
                date=month_start,
                in_prom=mean(s.in_prom for s in group),
                out_prom=mean(s.out_prom for s in group),
                in_max=max(s.in_max for s in group),
                out_max=max(s.out_max for s in group),
                use=max(s.use for s in group),
                device=device,
            )
            for device, group in grouped.items()
        ]
