from collections.abc import Callable
from pathlib import Path
from scanbackup.domain import (
    TrafficSourceBBIPField,
    TrafficSourceBBIPRepository,
    TrafficSourceBBIPEntity,
    BaseReader,
    BaseWriter,
)
from scanbackup.shared import CSVExportError, Log


class TrafficSourceUpdaterUseCase:
    _repo: TrafficSourceBBIPRepository
    _path: Path
    _reader: BaseReader
    _writer_factory: Callable[..., BaseWriter]

    def __init__(
        self,
        repository: TrafficSourceBBIPRepository,
        path: Path,
        reader: BaseReader,
        writer_factory: Callable[..., BaseWriter],
    ) -> None:
        self._repo = repository
        self._path = path
        self._reader = reader
        self._writer_factory = writer_factory

    def execute(self) -> None:
        sources: list[TrafficSourceBBIPEntity] = self._reader.import_data(self._path)
        present_keys = [
            {
                TrafficSourceBBIPField.INTERFACE.value: s.interface,
                TrafficSourceBBIPField.LAYER.value: s.layer,
                TrafficSourceBBIPField.MODEL.value: s.model,
            }
            for s in sources
        ]
        self._repo.upsert_sources(sources)
        self._repo.discontinue_missing(present_keys)

    def export(self, layers: list[str]) -> None:
        for layer in layers:
            try:
                layer = layer.upper()
                data = self._repo.get_sources_by_layer(layer)

                csv = self._writer_factory(dir=self._path)
                csv.export(
                    filename=layer,
                    data=data,
                    model=TrafficSourceBBIPEntity,
                    exclude={
                        "id",
                        TrafficSourceBBIPField.STATUS.value,
                        TrafficSourceBBIPField.COMMENTS.value,
                        TrafficSourceBBIPField.LAYER.value,
                    },
                )
            except CSVExportError:
                continue
            except Exception as error:
                Log.error(f"Error en exportación \n {error}")
                exit(1)
