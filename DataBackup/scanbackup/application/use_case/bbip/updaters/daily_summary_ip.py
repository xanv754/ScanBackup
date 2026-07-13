from collections import defaultdict
from datetime import date
from statistics import mean
from scanbackup.domain import (
    IPDailySummaryBBIPEntity,
    IPDailySummaryBBIPRepository,
    IPSourceBBIPEntity,
    IPActiveBBIPEntity,
)
from scanbackup.shared import PyObjectId


class IPDailySummaryUpdaterUseCase:
    _repo: IPDailySummaryBBIPRepository

    def __init__(self, repo: IPDailySummaryBBIPRepository) -> None:
        """Store the repository used to persist the computed daily summaries."""
        self._repo = repo

    def _group_by_device_and_date(
        self, samples: list[IPActiveBBIPEntity]
    ) -> dict[tuple[date, PyObjectId], list[IPActiveBBIPEntity]]:
        """Group raw samples by (date, device) so each group summarizes one device-day."""
        grouped: dict[tuple[date, PyObjectId], list[IPActiveBBIPEntity]] = defaultdict(
            list
        )
        for sample in samples:
            grouped[(sample.date, sample.device)].append(sample)
        return grouped

    def _build_summary(
        self,
        summary_date: date,
        device: PyObjectId,
        group: list[IPActiveBBIPEntity],
        sources_by_id: dict[PyObjectId, IPSourceBBIPEntity],
    ) -> IPDailySummaryBBIPEntity | None:
        """Aggregate one device-day group into a summary entity, or None if its source is unknown."""
        if device not in sources_by_id:
            return None

        in_prom = mean(sample.in_prom for sample in group)
        in_max = max(sample.in_max for sample in group)

        return IPDailySummaryBBIPEntity(
            date=summary_date, in_prom=in_prom, in_max=in_max, device=device
        )

    def execute(
        self,
        samples: list[IPActiveBBIPEntity],
        sources: list[IPSourceBBIPEntity],
    ) -> None:
        """Aggregate the raw samples of every device into one summary per device-day.

        Samples whose device has no matching source are dropped, matching the
        IP history use case's inner-join semantics.

        Args:
            samples (list[IPActiveBBIPEntity]): The raw active-IP samples to summarize.
            sources (list[IPSourceBBIPEntity]): The sources used to validate each
                sample's device.
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
