from scanbackup.domain import (
    IPHourSummaryBBIPRepository,
    IPSourceBBIPEntity,
    IPActiveBBIPEntity,
    IPSummaryService,
)


class IPHourSummaryUpdaterUseCase:
    _repo: IPHourSummaryBBIPRepository

    def __init__(self, repo: IPHourSummaryBBIPRepository) -> None:
        """Store the repository used to persist the computed hourly summaries."""
        self._repo = repo

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
        entities = IPSummaryService.summarize_by_hour(samples, sources)
        self._repo.insert(entities)
