from scanbackup.domain import (
    TrafficDailySummaryBBIPRepository,
    TrafficSourceBBIPEntity,
    TrafficBBIPEntity,
    TrafficSummaryService,
)


class TrafficDailySummaryUpdaterUseCase:
    _repo: TrafficDailySummaryBBIPRepository

    def __init__(self, repo: TrafficDailySummaryBBIPRepository) -> None:
        """Store the repository used to persist the computed daily summaries."""
        self._repo = repo

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
        entities = TrafficSummaryService.summarize_by_date(samples, sources)
        self._repo.insert(entities)
