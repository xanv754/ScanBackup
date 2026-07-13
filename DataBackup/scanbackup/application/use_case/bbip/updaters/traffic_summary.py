from datetime import date
from typing import Callable
from scanbackup.domain import (
    TrafficSourceBBIPRepository,
    TrafficHistoryBBIPRepository,
    TrafficDailySummaryBBIPRepository,
    TrafficBBIPEntity,
)
from scanbackup.application.use_case.bbip.updaters.daily_summary_traffic import (
    TrafficDailySummaryUpdaterUseCase,
)
from scanbackup.shared import UpdaterError

HistoryRepositoryFactory = Callable[[str], TrafficHistoryBBIPRepository]


class TrafficSummaryGeneratorUseCase:
    """Generates the daily traffic summary of every layer from its stored history."""

    _repo_sources: TrafficSourceBBIPRepository
    _history_repository_factory: HistoryRepositoryFactory
    _repo_daily: TrafficDailySummaryBBIPRepository
    _layers: list[str]
    _date: date

    def __init__(
        self,
        source_repository: TrafficSourceBBIPRepository,
        history_repository_factory: HistoryRepositoryFactory,
        daily_repository: TrafficDailySummaryBBIPRepository,
        layers: list[str],
        data_date: str,
    ) -> None:
        """Store the collaborators used to read the stored history and persist its summary.

        Args:
            source_repository (TrafficSourceBBIPRepository): Repository queried
                for every source's capacity, regardless of its status.
            history_repository_factory (HistoryRepositoryFactory): Builds the
                layer-specific history repository given a layer name.
            daily_repository (TrafficDailySummaryBBIPRepository): Repository
                used to persist the resulting daily summary.
            layers (list[str]): Every traffic layer whose stored history must
                be read.
            data_date (str): The day to summarize, formatted as YYYY-MM-DD.
        """
        self._repo_sources = source_repository
        self._history_repository_factory = history_repository_factory
        self._repo_daily = daily_repository
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
        """Generate the daily traffic summary of every layer from its stored history.

        Reads every configured layer's stored history for the target date,
        resolves each device's capacity from the sources collection
        (regardless of its current status), and persists one averaged
        summary per device.
        """
        try:
            samples = self._read_all_samples()
            if not samples:
                return

            sources = self._repo_sources.get_all_sources()

            daily_summary_use_case = TrafficDailySummaryUpdaterUseCase(self._repo_daily)
            daily_summary_use_case.execute(samples, sources)
        except Exception as error:
            raise UpdaterError(
                message="Error al generar el resumen diario de tráfico",
                error=error,
            )
