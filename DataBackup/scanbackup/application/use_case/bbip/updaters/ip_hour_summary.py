from datetime import date
from typing import Callable
from scanbackup.domain import (
    IPSourceBBIPRepository,
    IPHistoryBBIPRepository,
    IPHourSummaryBBIPRepository,
    IPActiveBBIPEntity,
)
from scanbackup.application.use_case.bbip.updaters.hour_summary_ip import (
    IPHourSummaryUpdaterUseCase,
)
from scanbackup.shared import UpdaterError

IPHistoryRepositoryFactory = Callable[[str], IPHistoryBBIPRepository]


class IPHourSummaryGeneratorUseCase:
    """Generates the hourly active-IP summary of every layer from its stored history."""

    _repo_sources: IPSourceBBIPRepository
    _history_repository_factory: IPHistoryRepositoryFactory
    _repo_hour: IPHourSummaryBBIPRepository
    _layers: list[str]
    _date: date

    def __init__(
        self,
        source_repository: IPSourceBBIPRepository,
        history_repository_factory: IPHistoryRepositoryFactory,
        hour_repository: IPHourSummaryBBIPRepository,
        layers: list[str],
        data_date: str,
    ) -> None:
        """Store the collaborators used to read the stored history and persist its summary.

        Args:
            source_repository (IPSourceBBIPRepository): Repository queried to
                validate each sample's device, regardless of its status.
            history_repository_factory (IPHistoryRepositoryFactory): Builds the
                layer-specific history repository given a layer name.
            hour_repository (IPHourSummaryBBIPRepository): Repository used to
                persist the resulting hourly summary.
            layers (list[str]): Every IP layer whose stored history must be read.
            data_date (str): The day to summarize, formatted as YYYY-MM-DD.
        """
        self._repo_sources = source_repository
        self._history_repository_factory = history_repository_factory
        self._repo_hour = hour_repository
        self._layers = layers
        self._date = date.fromisoformat(data_date)

    def _read_all_samples(self) -> list[IPActiveBBIPEntity]:
        """Read every configured layer's stored history for the target date."""
        samples: list[IPActiveBBIPEntity] = []
        for layer in self._layers:
            history_repository = self._history_repository_factory(layer)
            samples.extend(history_repository.get_by_date(self._date))
        return samples

    def execute(self) -> None:
        """Generate the hourly active-IP summary of every layer from its stored history.

        Reads every configured layer's stored history for the target date,
        validates each sample's device against the sources collection
        (regardless of its current status), groups the samples by the round
        hour they fall into, and persists one averaged summary per device-hour.
        """
        try:
            samples = self._read_all_samples()
            if not samples:
                return

            sources = self._repo_sources.get_all_sources()

            hour_summary_use_case = IPHourSummaryUpdaterUseCase(self._repo_hour)
            hour_summary_use_case.execute(samples, sources)
        except Exception as error:
            raise UpdaterError(
                message="Error al generar el resumen por hora de IP activas",
                error=error,
            )
