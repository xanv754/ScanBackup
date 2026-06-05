import csv
from pathlib import Path
from scanbackup.shared import DataContentError, Configuration
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.source import (
    TrafficSourceBBIPField,
)
from scanbackup.infrastructure.readers.reader import BaseReader


class TrafficSourceBBIPImport(BaseReader):
    _delimiter: str

    def __init__(self, delimiter: str | None = None) -> None:
        if not delimiter:
            system = Configuration()
            config = system.get_cfg_metadata()
            delimiter = config.scanner.file_delimiter
        self._delimiter = delimiter

    def import_data(self, filepath: Path) -> list:
        documents = []
        try:
            with filepath.open("r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=self._delimiter)
                for i, row in enumerate(reader, start=1):
                    document = {k: v for k, v in row.items() if k != "_id"}
                    try:
                        document[TrafficSourceBBIPField.CAPACITY.value] = float(
                            document[TrafficSourceBBIPField.CAPACITY.value]
                        )
                    except (ValueError, KeyError):
                        raise DataContentError(
                            extra_msg=f"Valor inválido de capacidad, línea {i}"
                        )

                    documents.append(document)
        except Exception as error:
            raise DataContentError(error=error)
        else:
            return documents


class IPSourceBBIPImport(BaseReader):
    _delimiter: str

    def __init__(self, delimiter: str | None = None) -> None:
        if not delimiter:
            system = Configuration()
            config = system.get_cfg_metadata()
            delimiter = config.scanner.file_delimiter
        self._delimiter = delimiter

    def import_data(self, filepath: Path) -> list:
        try:
            with filepath.open("r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=self._delimiter)
                documents = [
                    {k: v for k, v in row.items() if k != "_id"} for row in reader
                ]
        except Exception as error:
            raise DataContentError(error=error)
        else:
            return documents
