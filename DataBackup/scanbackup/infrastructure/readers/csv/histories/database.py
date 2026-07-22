import csv
from pathlib import Path
from bson import ObjectId
from bson.errors import InvalidId
from scanbackup.shared import DataContentError, FileEmptyError, Configuration
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.data import (
    TrafficBBIPField,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.ip.active import (
    IPActiveBBIPField,
)
from scanbackup.domain import BaseReader


class TrafficHistoryBBIPImport(BaseReader):
    _delimiter: str

    def __init__(self, delimiter: str | None = None) -> None:
        if not delimiter:
            system = Configuration()
            config = system.get_cfg_metadata()
            delimiter = config.scanner.file_delimiter
        self._delimiter = delimiter

    def import_data(self, filepath: Path) -> list[dict]:
        if filepath.stat().st_size == 0:
            raise FileEmptyError(filepath=str(filepath.resolve()))

        with filepath.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=self._delimiter)
            rows = []
            for i, row in enumerate(reader, start=1):
                try:
                    row[TrafficBBIPField.DEVICE.value] = ObjectId(
                        row[TrafficBBIPField.DEVICE.value]
                    )
                except (ValueError, KeyError, InvalidId):
                    raise DataContentError(extra_msg=f"Valor inválido de id, línea {i}")

                float_fields = [
                    (TrafficBBIPField.IN_MAX, "in max"),
                    (TrafficBBIPField.IN_PROM, "in prom"),
                    (TrafficBBIPField.OUT_MAX, "out max"),
                    (TrafficBBIPField.OUT_PROM, "out prom"),
                ]
                for field, label in float_fields:
                    try:
                        row[field.value] = float(row[field.value])
                    except (ValueError, KeyError):
                        raise DataContentError(
                            extra_msg=f"Valor inválido de {label}, línea {i}"
                        )

                rows.append(row)

        return rows


class IPHistoryBBIPImport(BaseReader):
    _delimiter: str

    def __init__(self, delimiter: str | None = None) -> None:
        if not delimiter:
            system = Configuration()
            config = system.get_cfg_metadata()
            delimiter = config.scanner.file_delimiter
        self._delimiter = delimiter

    def import_data(self, filepath: Path) -> list[dict]:
        if filepath.stat().st_size == 0:
            raise FileEmptyError(filepath=str(filepath.resolve()))

        with filepath.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=self._delimiter)
            rows = []
            for i, row in enumerate(reader, start=1):
                try:
                    row[IPActiveBBIPField.DEVICE.value] = ObjectId(
                        row[IPActiveBBIPField.DEVICE.value]
                    )
                except (ValueError, KeyError, InvalidId):
                    raise DataContentError(extra_msg=f"Valor inválido de id, línea {i}")

                try:
                    row[IPActiveBBIPField.IN_MAX] = float(
                        row[IPActiveBBIPField.IN_MAX.value]
                    )
                except (ValueError, KeyError):
                    raise DataContentError(
                        extra_msg=f"Valor inválido de in max, línea {i}"
                    )

                try:
                    row[IPActiveBBIPField.IN_PROM] = float(
                        row[IPActiveBBIPField.IN_PROM.value]
                    )
                except (ValueError, KeyError):
                    raise DataContentError(
                        extra_msg=f"Valor inválido de in prom, línea {i}"
                    )
                rows.append(row)

        return rows
