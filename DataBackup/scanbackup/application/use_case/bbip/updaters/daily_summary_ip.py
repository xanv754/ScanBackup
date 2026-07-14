from scanbackup.domain import (
    IPDailySummaryBBIPRepository,
    IPSourceBBIPEntity,
    IPActiveBBIPEntity,
    IPSummaryService,
)


class IPDailySummaryUpdaterUseCase:
    _repo: IPDailySummaryBBIPRepository

    def __init__(self, repo: IPDailySummaryBBIPRepository) -> None:
        """Store the repository used to persist the computed daily summaries."""
        self._repo = repo

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
        entities = IPSummaryService.summarize_by_date(samples, sources)
        self._repo.insert(entities)
