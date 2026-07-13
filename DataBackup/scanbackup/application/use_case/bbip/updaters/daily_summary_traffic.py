from collections import defaultdict
from datetime import date
from statistics import mean
from scanbackup.domain import (
    TrafficDailySummaryBBIPEntity,
    TrafficDailySummaryBBIPRepository,
    TrafficSourceBBIPEntity,
    TrafficBBIPEntity,
)
from scanbackup.shared import PyObjectId

FACTOR_BBIP: float = 0.000000008022


class TrafficDailySummaryUpdaterUseCase:
    _repo: TrafficDailySummaryBBIPRepository

    def __init__(self, repo: TrafficDailySummaryBBIPRepository) -> None:
        """Store the repository used to persist the computed daily summaries."""
        self._repo = repo

    def _group_by_device_and_date(
        self, samples: list[TrafficBBIPEntity]
    ) -> dict[tuple[date, PyObjectId], list[TrafficBBIPEntity]]:
        """Group raw samples by (date, device) so each group summarizes one device-day."""
        grouped: dict[tuple[date, PyObjectId], list[TrafficBBIPEntity]] = defaultdict(
            list
        )
        for sample in samples:
            grouped[(sample.date, sample.device)].append(sample)
        return grouped

    def _build_summary(
        self,
        summary_date: date,
        device: PyObjectId,
        group: list[TrafficBBIPEntity],
        sources_by_id: dict[PyObjectId, TrafficSourceBBIPEntity],
    ) -> TrafficDailySummaryBBIPEntity | None:
        """Aggregate one device-day group into a summary entity, or None if its source is unknown."""
        source = sources_by_id.get(device)
        if not source:
            return None

        in_prom = mean(sample.in_prom for sample in group) * FACTOR_BBIP
        out_prom = mean(sample.out_prom for sample in group) * FACTOR_BBIP
        in_max = max(sample.in_max for sample in group) * FACTOR_BBIP
        out_max = max(sample.out_max for sample in group) * FACTOR_BBIP
        use = max(in_max, out_max) / source.capacity * 100

        return TrafficDailySummaryBBIPEntity(
            date=summary_date,
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
        """Aggregate the raw samples of every device into one summary per device-day.

        Samples whose device has no matching source are dropped, matching the
        traffic history use case's inner-join semantics.

        Args:
            samples (list[TrafficBBIPEntity]): The raw traffic samples to summarize.
            sources (list[TrafficSourceBBIPEntity]): The sources used to look up
                each device's capacity.
        """
        sources_by_id = {source.id: source for source in sources}
        grouped = self._group_by_device_and_date(samples)

        entities = [
            entity
            for (summary_date, device), group in grouped.items()
            if (entity := self._build_summary(summary_date, device, group, sources_by_id))
            is not None
        ]

        self._repo.insert(entities)
