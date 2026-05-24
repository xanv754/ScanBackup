import csv
from pathlib import Path
from scanbackup.domain.entities.bbip.traffic.source import BBIPTrafficSourceEntity
from scanbackup.shared import BBIPTrafficSourceHeader, ContentFileError, Configuration


class BBIPTrafficSourceMapper:
    @staticmethod
    def from_csv(filepath: Path) -> list[BBIPTrafficSourceEntity]:
        system = Configuration()
        config = system.get_cfg_metadata().scanner

        layer = filepath.stem.upper()
        sources = []

        with filepath.open(newline="", encoding="utf-8") as f:
            try:
                reader = csv.DictReader(f, delimiter=config.file_delimiter)
                for row in reader:
                    sources.append(
                        BBIPTrafficSourceEntity(
                            link=row[BBIPTrafficSourceHeader.LINK.value],
                            interface=row[BBIPTrafficSourceHeader.INTERFACE.value],
                            capacity=float(row[BBIPTrafficSourceHeader.CAPACITY.value]),
                            type=row[BBIPTrafficSourceHeader.TYPE.value],
                            layer=layer,
                        )
                    )
            except Exception as error:
                raise ContentFileError(filepath=filepath.resolve(), error=error)

        return sources
