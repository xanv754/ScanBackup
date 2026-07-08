import csv
from pathlib import Path
from scanbackup.domain.entities.bbip.traffic.source import TrafficSourceBBIPEntity
from scanbackup.shared import TrafficSourceBBIPHeader, ContentFileError, Configuration


class BBIPTrafficSourceMapper:
    @staticmethod
    def from_csv(filepath: Path) -> list[TrafficSourceBBIPEntity]:
        system = Configuration()
        config = system.get_cfg_metadata().scanner

        layer = filepath.stem.upper()
        sources = []

        with filepath.open(newline="", encoding="utf-8") as f:
            try:
                reader = csv.DictReader(f, delimiter=config.file_delimiter)
                for row in reader:
                    sources.append(
                        TrafficSourceBBIPEntity(
                            link=row[TrafficSourceBBIPHeader.LINK.value],
                            interface=row[TrafficSourceBBIPHeader.INTERFACE.value],
                            capacity=float(row[TrafficSourceBBIPHeader.CAPACITY.value]),
                            model=row[TrafficSourceBBIPHeader.TYPE.value],
                            layer=layer,
                        )
                    )
            except Exception as error:
                raise ContentFileError(filepath=str(filepath.resolve()), error=error)

        return sources
