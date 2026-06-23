from pathlib import Path
from scanbackup.domain import (
    TrafficSourceBBIPField,
    TrafficSourceBBIPRepository,
    TrafficSourceBBIPEntity,
)
from scanbackup.infrastructure import TrafficSourceBBIPReader, CSVWriter
from scanbackup.shared import CSVExportError, Log


class TrafficSourceUpdaterUseCase:
    _repo: TrafficSourceBBIPRepository
    _path: Path

    def __init__(self, repository: TrafficSourceBBIPRepository, path: Path) -> None:
        self._repo = repository
        self._path = path

    def execute(self) -> None:
        reader = TrafficSourceBBIPReader()
        sources: list[TrafficSourceBBIPEntity] = reader.import_data(self._path)
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

                csv = CSVWriter(dir=self._path)
                csv.export(
                    filename=layer,
                    data=data,
                    exclude={
                        "device",
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
