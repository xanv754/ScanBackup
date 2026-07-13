from collections import defaultdict
from datetime import date, time
from statistics import mean
from scanbackup.domain import (
    IPHourSummaryBBIPEntity,
    IPHourSummaryBBIPRepository,
    IPSourceBBIPEntity,
    IPActiveBBIPEntity,
)
from scanbackup.shared import PyObjectId


class IPHourSummaryUpdaterUseCase:
    _repo: IPHourSummaryBBIPRepository

    def __init__(self, repo: IPHourSummaryBBIPRepository) -> None:
        """Store the repository used to persist the computed hourly summaries."""
        self._repo = repo

    @staticmethod
    def _round_down_to_hour(sample_time: time) -> time:
        """Truncate a time value to its enclosing round hour (e.g. 13:37:12 -> 13:00:00)."""
        return sample_time.replace(minute=0, second=0, microsecond=0)

    def _group_by_device_date_and_hour(
        self, samples: list[IPActiveBBIPEntity]
    ) -> dict[tuple[date, time, PyObjectId], list[IPActiveBBIPEntity]]:
        """Group raw samples by (date, hour, device) so each group summarizes one device-hour."""
        grouped: dict[
            tuple[date, time, PyObjectId], list[IPActiveBBIPEntity]
        ] = defaultdict(list)
        for sample in samples:
            hour = self._round_down_to_hour(sample.time)
            grouped[(sample.date, hour, sample.device)].append(sample)
        return grouped

    def _build_summary(
        self,
        summary_date: date,
        summary_hour: time,
        device: PyObjectId,
        group: list[IPActiveBBIPEntity],
        sources_by_id: dict[PyObjectId, IPSourceBBIPEntity],
    ) -> IPHourSummaryBBIPEntity | None:
        """Aggregate one device-hour group into a summary entity, or None if its source is unknown."""
        if device not in sources_by_id:
            return None

        in_prom = mean(sample.in_prom for sample in group)
        in_max = max(sample.in_max for sample in group)

        return IPHourSummaryBBIPEntity(
            date=summary_date, time=summary_hour, in_prom=in_prom, in_max=in_max, device=device
        )

    def execute(
        self,
        samples: list[IPActiveBBIPEntity],
        sources: list[IPSourceBBIPEntity],
    ) -> None:
        """Aggregate the raw samples of every device into one summary per device-hour.

        Samples whose device has no matching source are dropped, matching the
        IP history use case's inner-join semantics.

        Args:
            samples (list[IPActiveBBIPEntity]): The raw active-IP samples to summarize.
            sources (list[IPSourceBBIPEntity]): The sources used to validate each
                sample's device.
        """
        sources_by_id = {source.id: source for source in sources}
        grouped = self._group_by_device_date_and_hour(samples)

        entities = [
            entity
            for (summary_date, summary_hour, device), group in grouped.items()
            if (
                entity := self._build_summary(
                    summary_date, summary_hour, device, group, sources_by_id
                )
            )
            is not None
        ]

        self._repo.insert(entities)
