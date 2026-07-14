from collections import defaultdict
from datetime import date, time
from statistics import mean
from scanbackup.domain.entities.bbip.traffic.data import TrafficBBIPEntity
from scanbackup.domain.entities.bbip.traffic.source import TrafficSourceBBIPEntity
from scanbackup.domain.entities.bbip.traffic.summaries.daily import (
    TrafficDailySummaryBBIPEntity,
)
from scanbackup.domain.entities.bbip.traffic.summaries.hour import (
    TrafficHourSummaryBBIPEntity,
)
from scanbackup.shared import PyObjectId

FACTOR_BBIP: float = 0.000000008022


def _group_by_device_and_date(
    samples: list[TrafficBBIPEntity],
) -> dict[tuple[date, PyObjectId], list[TrafficBBIPEntity]]:
    """Group raw samples by (date, device) so each group summarizes one device-day."""
    grouped: dict[tuple[date, PyObjectId], list[TrafficBBIPEntity]] = defaultdict(list)
    for sample in samples:
        grouped[(sample.date, sample.device)].append(sample)
    return grouped


def _round_down_to_hour(sample_time: time) -> time:
    """Truncate a time value to its enclosing round hour (e.g. 13:37:12 -> 13:00:00)."""
    return sample_time.replace(minute=0, second=0, microsecond=0)


def _group_by_device_date_and_hour(
    samples: list[TrafficBBIPEntity],
) -> dict[tuple[date, time, PyObjectId], list[TrafficBBIPEntity]]:
    """Group raw samples by (date, hour, device) so each group summarizes one device-hour."""
    grouped: dict[tuple[date, time, PyObjectId], list[TrafficBBIPEntity]] = defaultdict(
        list
    )
    for sample in samples:
        hour = _round_down_to_hour(sample.time)
        grouped[(sample.date, hour, sample.device)].append(sample)
    return grouped


class TrafficSummaryService:
    """Aggregates raw traffic samples into daily/hourly summaries using SCAN's BBIP conversion rules."""

    @staticmethod
    def summarize_by_date(
        samples: list[TrafficBBIPEntity],
        sources: list[TrafficSourceBBIPEntity],
    ) -> list[TrafficDailySummaryBBIPEntity]:
        """Aggregate raw samples into one daily summary per device, dropping samples with no matching source."""
        sources_by_id = {source.id: source for source in sources}
        grouped = _group_by_device_and_date(samples)

        entities = []
        for (summary_date, device), group in grouped.items():
            source = sources_by_id.get(device)
            if not source:
                continue

            in_prom = mean(sample.in_prom for sample in group) * FACTOR_BBIP
            out_prom = mean(sample.out_prom for sample in group) * FACTOR_BBIP
            in_max = max(sample.in_max for sample in group) * FACTOR_BBIP
            out_max = max(sample.out_max for sample in group) * FACTOR_BBIP
            use = max(in_max, out_max) / source.capacity * 100

            entities.append(
                TrafficDailySummaryBBIPEntity(
                    date=summary_date,
                    in_prom=in_prom,
                    out_prom=out_prom,
                    in_max=in_max,
                    out_max=out_max,
                    use=use,
                    device=device,
                )
            )
        return entities

    @staticmethod
    def summarize_by_hour(
        samples: list[TrafficBBIPEntity],
        sources: list[TrafficSourceBBIPEntity],
    ) -> list[TrafficHourSummaryBBIPEntity]:
        """Aggregate raw samples into one hourly summary per device, dropping samples with no matching source."""
        sources_by_id = {source.id: source for source in sources}
        grouped = _group_by_device_date_and_hour(samples)

        entities = []
        for (summary_date, summary_hour, device), group in grouped.items():
            source = sources_by_id.get(device)
            if not source:
                continue

            in_prom = mean(sample.in_prom for sample in group) * FACTOR_BBIP
            out_prom = mean(sample.out_prom for sample in group) * FACTOR_BBIP
            in_max = max(sample.in_max for sample in group) * FACTOR_BBIP
            out_max = max(sample.out_max for sample in group) * FACTOR_BBIP
            use = max(in_max, out_max) / source.capacity * 100

            entities.append(
                TrafficHourSummaryBBIPEntity(
                    date=summary_date,
                    time=summary_hour,
                    in_prom=in_prom,
                    out_prom=out_prom,
                    in_max=in_max,
                    out_max=out_max,
                    use=use,
                    device=device,
                )
            )
        return entities
