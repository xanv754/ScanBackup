from pathlib import Path
from scanbackup.domain import TrafficBBIPSourceRepository
from scanbackup.application.mappers.traffic_bbip_source import (
    BBIPTrafficSourceMapper,
)


class UpdateBBIPSources:
    _repo: TrafficBBIPSourceRepository
    _filepath: Path

    def __init__(self, repository: TrafficBBIPSourceRepository, filepath: Path) -> None:
        self._repo = repository
        self._filepath = filepath

    def execute(self) -> None:
        sources = BBIPTrafficSourceMapper.from_csv(self._filepath)
        present_keys = [
            {"interface": s.interface, "layer": s.layer, "type": s.type}
            for s in sources
        ]
        self._repo.upsert_sources(sources)
        self._repo.discontinue_missing(present_keys)
