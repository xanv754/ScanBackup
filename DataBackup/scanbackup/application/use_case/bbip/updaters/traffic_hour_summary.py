from datetime import date
from typing import Callable
from scanbackup.domain import (
    TrafficSourceBBIPRepository,
    TrafficHistoryBBIPRepository,
    TrafficHourSummaryBBIPRepository,
    TrafficBBIPEntity,
)
from scanbackup.application.use_case.bbip.updaters.hour_summary_traffic import (
    TrafficHourSummaryUpdaterUseCase,
)
from scanbackup.shared import UpdaterError

HistoryRepositoryFactory = Callable[[str], TrafficHistoryBBIPRepository]


class TrafficHourSummaryGeneratorUseCase:
    """Generates the hourly traffic summary of every layer from its stored history."""

    _repo_sources: TrafficSourceBBIPRepository
    _history_repository_factory: HistoryRepositoryFactory
    _repo_hour: TrafficHourSummaryBBIPRepository
    _layers: list[str]
    _date: date

    def __init__(
        self,
        source_repository: TrafficSourceBBIPRepository,
        history_repository_factory: HistoryRepositoryFactory,
        hour_repository: TrafficHourSummaryBBIPRepository,
        layers: list[str],
        data_date: str,
    ) -> None:
        """Store the collaborators used to read the stored history and persist its summary.

        Args:
            source_repository (TrafficSourceBBIPRepository): Repository queried
                for every source's capacity, regardless of its status.
            history_repository_factory (HistoryRepositoryFactory): Builds the
                layer-specific history repository given a layer name.
            hour_repository (TrafficHourSummaryBBIPRepository): Repository used
                to persist the resulting hourly summary.
            layers (list[str]): Every traffic layer whose stored history must
                be read.
            data_date (str): The day to summarize, formatted as YYYY-MM-DD.
        """
        self._repo_sources = source_repository
        self._history_repository_factory = history_repository_factory
        self._repo_hour = hour_repository
        self._layers = layers
        self._date = date.fromisoformat(data_date)

    def _read_all_samples(self) -> list[TrafficBBIPEntity]:
        """Read every configured layer's stored history for the target date."""
        samples: list[TrafficBBIPEntity] = []
        for layer in self._layers:
            history_repository = self._history_repository_factory(layer)
            samples.extend(history_repository.get_by_date(self._date))
        return samples

    def execute(self) -> None:
        """Generate the hourly traffic summary of every layer from its stored history.

        Reads every configured layer's stored history for the target date,
        resolves each device's capacity from the sources collection
        (regardless of its current status), groups the samples by the round
        hour they fall into, and persists one averaged summary per device-hour.
        """
        try:
            samples = self._read_all_samples()
            if not samples:
                return

            sources = self._repo_sources.get_all_sources()

            hour_summary_use_case = TrafficHourSummaryUpdaterUseCase(self._repo_hour)
            hour_summary_use_case.execute(samples, sources)
        except Exception as error:
            raise UpdaterError(
                message="Error al generar el resumen por hora de tráfico",
                error=error,
            )
