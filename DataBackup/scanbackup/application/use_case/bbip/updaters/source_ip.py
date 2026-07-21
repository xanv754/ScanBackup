from collections.abc import Callable
from pathlib import Path
from scanbackup.domain import (
    IPSourceBBIPField,
    IPSourceBBIPRepository,
    IPSourceBBIPEntity,
)
from scanbackup.infrastructure.readers.reader import BaseReader
from scanbackup.infrastructure.writers.writer import BaseWriter
from scanbackup.shared import CSVExportError, Log


class IPSourceUpdaterUseCase:
    _repo: IPSourceBBIPRepository
    _path: Path
    _reader: BaseReader
    _writer_factory: Callable[..., BaseWriter]

    def __init__(
        self,
        repository: IPSourceBBIPRepository,
        path: Path,
        reader: BaseReader,
        writer_factory: Callable[..., BaseWriter],
    ) -> None:
        self._repo = repository
        self._path = path
        self._reader = reader
        self._writer_factory = writer_factory

    def execute(self) -> None:
        sources: list[IPSourceBBIPEntity] = self._reader.import_data(self._path)
        present_keys = [
            {
                IPSourceBBIPField.INTERFACE.value: s.interface,
                IPSourceBBIPField.LAYER.value: s.layer,
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
                    model=IPSourceBBIPEntity,
                    exclude={
                        "id",
                        IPSourceBBIPField.STATUS.value,
                        IPSourceBBIPField.LAYER.value,
                    },
                )
            except CSVExportError:
                continue
            except Exception as error:
                Log.error(f"Error en exportación \n {error}")
                exit(1)
