from pathlib import Path
from scanbackup.domain import (
    IPSourceBBIPField,
    IPSourceBBIPRepository,
    IPSourceBBIPEntity,
)
from scanbackup.infrastructure import IPSourceBBIPReader, CSVWriter
from scanbackup.shared import CSVExportError, Log


class IPSourceUpdaterUseCase:
    _repo: IPSourceBBIPRepository
    _path: Path

    def __init__(self, repository: IPSourceBBIPRepository, path: Path) -> None:
        self._repo = repository
        self._path = path

    def execute(self) -> None:
        reader = IPSourceBBIPReader()
        sources: list[IPSourceBBIPEntity] = reader.import_data(self._path)
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

                csv = CSVWriter(dir=self._path)
                csv.export(
                    filename=layer,
                    data=data,
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
