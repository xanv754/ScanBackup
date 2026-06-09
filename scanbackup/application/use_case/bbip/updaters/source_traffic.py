from pathlib import Path
from scanbackup.domain import TrafficSourceBBIPRepository
from scanbackup.infrastructure import TrafficSourceBBIPReader
from scanbackup.infrastructure import CSVWriter
from scanbackup.shared import CSVExportError, Log


class UpdateBBIPSources:
    _repo: TrafficSourceBBIPRepository
    _path: Path

    def __init__(self, repository: TrafficSourceBBIPRepository, path: Path) -> None:
        self._repo = repository
        self._path = path

    def upload(self) -> None:
        sources = TrafficSourceBBIPReader.import_data(self._path)
        present_keys = [
            {"interface": s.interface, "layer": s.layer, "type": s.type}
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
                csv.export(filename=layer, data=data)
            except CSVExportError:
                continue
            except Exception as error:
                Log.error(f"Error en exportación \n {error}")
                exit(1)
