from collections import defaultdict
from datetime import date, time
from statistics import mean
from scanbackup.domain import (
    TrafficHourSummaryBBIPEntity,
    TrafficHourSummaryBBIPRepository,
    TrafficSourceBBIPEntity,
    TrafficBBIPEntity,
)
from scanbackup.shared import PyObjectId

FACTOR_BBIP: float = 0.000000008022


class TrafficHourSummaryUpdaterUseCase:
    _repo: TrafficHourSummaryBBIPRepository

    def __init__(self, repo: TrafficHourSummaryBBIPRepository) -> None:
        """Store the repository used to persist the computed hourly summaries."""
        self._repo = repo

    @staticmethod
    def _round_down_to_hour(sample_time: time) -> time:
        """Truncate a time value to its enclosing round hour (e.g. 13:37:12 -> 13:00:00)."""
        return sample_time.replace(minute=0, second=0, microsecond=0)

    def _group_by_device_date_and_hour(
        self, samples: list[TrafficBBIPEntity]
    ) -> dict[tuple[date, time, PyObjectId], list[TrafficBBIPEntity]]:
        """Group raw samples by (date, hour, device) so each group summarizes one device-hour."""
        grouped: dict[
            tuple[date, time, PyObjectId], list[TrafficBBIPEntity]
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
        group: list[TrafficBBIPEntity],
        sources_by_id: dict[PyObjectId, TrafficSourceBBIPEntity],
    ) -> TrafficHourSummaryBBIPEntity | None:
        """Aggregate one device-hour group into a summary entity, or None if its source is unknown."""
        source = sources_by_id.get(device)
        if not source:
            return None

        in_prom = mean(sample.in_prom for sample in group) * FACTOR_BBIP
        out_prom = mean(sample.out_prom for sample in group) * FACTOR_BBIP
        in_max = max(sample.in_max for sample in group) * FACTOR_BBIP
        out_max = max(sample.out_max for sample in group) * FACTOR_BBIP
        use = max(in_max, out_max) / source.capacity * 100

        return TrafficHourSummaryBBIPEntity(
            date=summary_date,
            time=summary_hour,
            in_prom=in_prom,
            out_prom=out_prom,
            in_max=in_max,
            out_max=out_max,
            use=use,
            device=device,
        )

    def execute(
        self,
        samples: list[TrafficBBIPEntity],
        sources: list[TrafficSourceBBIPEntity],
    ) -> None:
        """Aggregate the raw samples of every device into one summary per device-hour.

        Samples whose device has no matching source are dropped, matching the
        traffic history use case's inner-join semantics.

        Args:
            samples (list[TrafficBBIPEntity]): The raw traffic samples to summarize.
            sources (list[TrafficSourceBBIPEntity]): The sources used to look up
                each device's capacity.
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
