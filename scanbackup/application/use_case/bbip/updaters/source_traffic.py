from pathlib import Path
from scanbackup.domain import BBIPTrafficSourceRepository
from scanbackup.application.mappers.bbip.source_traffic import BBIPTrafficSourceMapper
from scanbackup.infrastructure import CSVExporter


class UpdateBBIPSources:
    _repo: BBIPTrafficSourceRepository
    _path: Path

    def __init__(self, repository: BBIPTrafficSourceRepository, path: Path) -> None:
        self._repo = repository
        self._path = path

    def upload(self) -> None:
        sources = BBIPTrafficSourceMapper.from_csv(self._path)
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
                csv = CSVExporter()
                csv.export(filename=layer, data=data)
            except Exception:
                continue
