from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Callable
from scanbackup.domain import (
    TrafficSourceBBIPRepository,
    TrafficHistoryBBIPRepository,
    TrafficSourceBBIPEntity,
    TrafficBBIPEntity,
)
from scanbackup.infrastructure.collectors import MRTGFetcher
from scanbackup.shared import ScannerError, UpdaterError

HistoryRepositoryFactory = Callable[[str], TrafficHistoryBBIPRepository]


class TrafficCollectorUseCase:
    """Fetches SCAN traffic for every active source and stores it in the system."""

    _repo_sources: TrafficSourceBBIPRepository
    _history_repository_factory: HistoryRepositoryFactory
    _fetcher: MRTGFetcher
    _date: date
    _max_workers: int

    def __init__(
        self,
        source_repository: TrafficSourceBBIPRepository,
        history_repository_factory: HistoryRepositoryFactory,
        fetcher: MRTGFetcher,
        data_date: str,
        max_workers: int = 1,
    ) -> None:
        """Store the collaborators used to fetch SCAN traffic and persist it.

        Args:
            source_repository (TrafficSourceBBIPRepository): Repository queried
                for every active source across all layers.
            history_repository_factory (HistoryRepositoryFactory): Builds the
                layer-specific history repository given a layer name.
            fetcher (MRTGFetcher): Downloads and parses a source's SCAN traffic.
            data_date (str): The day to collect, formatted as YYYY-MM-DD.
            max_workers (int): Maximum number of sources fetched concurrently.
        """
        self._repo_sources = source_repository
        self._history_repository_factory = history_repository_factory
        self._fetcher = fetcher
        self._date = date.fromisoformat(data_date)
        self._max_workers = max_workers

    def _fetch_source(
        self, source: TrafficSourceBBIPEntity
    ) -> tuple[str, list[TrafficBBIPEntity]]:
        """Fetch one source's traffic samples, isolating its failure from the rest of the batch."""
        try:
            return source.layer, self._fetcher.fetch(source, self._date)
        except Exception as error:
            ScannerError(error=error, layer=f"{source.layer}/{source.interface}")
            return source.layer, []

    def _fetch_all(
        self, sources: list[TrafficSourceBBIPEntity]
    ) -> dict[str, list[TrafficBBIPEntity]]:
        """Fetch every source concurrently, grouping the resulting samples by layer."""
        samples_by_layer: dict[str, list[TrafficBBIPEntity]] = defaultdict(list)
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = [
                executor.submit(self._fetch_source, source) for source in sources
            ]
            for future in as_completed(futures):
                layer, samples = future.result()
                samples_by_layer[layer].extend(samples)
        return samples_by_layer

    def execute(self) -> None:
        """Fetch the SCAN traffic of every active source and persist it in the system.

        Queries every active traffic source across all layers, fetches its
        SCAN traffic for the configured date, and inserts the raw samples into
        each layer's history collection. The daily summary is generated
        separately, from the stored history, by TrafficSummaryGeneratorUseCase.
        """
        try:
            sources = self._repo_sources.get_all_active_sources()
            if not sources:
                return

            samples_by_layer = self._fetch_all(sources)

            for layer, samples in samples_by_layer.items():
                if not samples:
                    continue
                history_repository = self._history_repository_factory(layer)
                history_repository.insert(samples)
        except Exception as error:
            raise UpdaterError(
                message="Error al recolectar los datos históricos de tráfico",
                error=error,
            )
