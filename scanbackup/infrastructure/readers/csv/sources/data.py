import csv
from pathlib import Path
from scanbackup.domain import TrafficSourceBBIPEntity, ValidatorConfig
from scanbackup.shared import (
    DataImportError,
    TrafficSourceBBIPHeader,
    ContentFileError,
    LayerNotDefined,
    Configuration,
)
from scanbackup.infrastructure.readers.reader import BaseReader


class TrafficSourceBBIPReader(BaseReader):
    def import_data(self, filepath: Path) -> list:
        try:
            system = Configuration()
            config = system.get_cfg_metadata().scanner

            layer = filepath.stem.upper()
            if not ValidatorConfig.valid_layer_bbip(layer):
                raise LayerNotDefined(layer)

            sources = []
            with filepath.open("r", newline="", encoding="utf-8") as f:
                try:
                    reader = csv.DictReader(f, delimiter=config.file_delimiter)
                    for row in reader:
                        sources.append(
                            TrafficSourceBBIPEntity(
                                link=row[TrafficSourceBBIPHeader.LINK.value],
                                interface=row[TrafficSourceBBIPHeader.INTERFACE.value],
                                capacity=float(
                                    row[TrafficSourceBBIPHeader.CAPACITY.value]
                                ),
                                model=row[TrafficSourceBBIPHeader.TYPE.value],
                                layer=layer,
                            )
                        )
                except Exception as error:
                    raise ContentFileError(
                        filepath=str(filepath.resolve()), error=error
                    )
            return sources
        except Exception as error:
            raise DataImportError(
                extra_msg=f"Fallo al importar el archivo {filepath}", error=error
            )
