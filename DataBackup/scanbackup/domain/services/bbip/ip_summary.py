from collections import defaultdict
from datetime import date, time
from statistics import mean
from scanbackup.domain.entities.bbip.ip.data import IPActiveBBIPEntity
from scanbackup.domain.entities.bbip.ip.source import IPSourceBBIPEntity
from scanbackup.domain.entities.bbip.ip.summaries.daily import IPDailySummaryBBIPEntity
from scanbackup.domain.entities.bbip.ip.summaries.hour import IPHourSummaryBBIPEntity
from scanbackup.shared import PyObjectId


def _group_by_device_and_date(
    samples: list[IPActiveBBIPEntity],
) -> dict[tuple[date, PyObjectId], list[IPActiveBBIPEntity]]:
    """Group raw samples by (date, device) so each group summarizes one device-day."""
    grouped: dict[tuple[date, PyObjectId], list[IPActiveBBIPEntity]] = defaultdict(list)
    for sample in samples:
        grouped[(sample.date, sample.device)].append(sample)
    return grouped


def _round_down_to_hour(sample_time: time) -> time:
    """Truncate a time value to its enclosing round hour (e.g. 13:37:12 -> 13:00:00)."""
    return sample_time.replace(minute=0, second=0, microsecond=0)


def _group_by_device_date_and_hour(
    samples: list[IPActiveBBIPEntity],
) -> dict[tuple[date, time, PyObjectId], list[IPActiveBBIPEntity]]:
    """Group raw samples by (date, hour, device) so each group summarizes one device-hour."""
    grouped: dict[tuple[date, time, PyObjectId], list[IPActiveBBIPEntity]] = defaultdict(
        list
    )
    for sample in samples:
        hour = _round_down_to_hour(sample.time)
        grouped[(sample.date, hour, sample.device)].append(sample)
    return grouped


class IPSummaryService:
    """Aggregates raw active-IP samples into daily/hourly summaries."""

    @staticmethod
    def summarize_by_date(
        samples: list[IPActiveBBIPEntity],
        sources: list[IPSourceBBIPEntity],
    ) -> list[IPDailySummaryBBIPEntity]:
        """Aggregate raw samples into one daily summary per device, dropping samples with no matching source."""
        sources_by_id = {source.id: source for source in sources}
        grouped = _group_by_device_and_date(samples)

        entities = []
        for (summary_date, device), group in grouped.items():
            if device not in sources_by_id:
                continue

            in_prom = mean(sample.in_prom for sample in group)
            in_max = max(sample.in_max for sample in group)

            entities.append(
                IPDailySummaryBBIPEntity(
                    date=summary_date, in_prom=in_prom, in_max=in_max, device=device
                )
            )
        return entities

    @staticmethod
    def summarize_by_hour(
        samples: list[IPActiveBBIPEntity],
        sources: list[IPSourceBBIPEntity],
    ) -> list[IPHourSummaryBBIPEntity]:
        """Aggregate raw samples into one hourly summary per device, dropping samples with no matching source."""
        sources_by_id = {source.id: source for source in sources}
        grouped = _group_by_device_date_and_hour(samples)

        entities = []
        for (summary_date, summary_hour, device), group in grouped.items():
            if device not in sources_by_id:
                continue

            in_prom = mean(sample.in_prom for sample in group)
            in_max = max(sample.in_max for sample in group)

            entities.append(
                IPHourSummaryBBIPEntity(
                    date=summary_date,
                    time=summary_hour,
                    in_prom=in_prom,
                    in_max=in_max,
                    device=device,
                )
            )
        return entities
