from scanbackup.domain import (
    TrafficHourSummaryBBIPRepository,
    TrafficSourceBBIPEntity,
    TrafficBBIPEntity,
    TrafficSummaryService,
)


class TrafficHourSummaryUpdaterUseCase:
    _repo: TrafficHourSummaryBBIPRepository

    def __init__(self, repo: TrafficHourSummaryBBIPRepository) -> None:
        """Store the repository used to persist the computed hourly summaries."""
        self._repo = repo

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
        entities = TrafficSummaryService.summarize_by_hour(samples, sources)
        self._repo.insert(entities)
