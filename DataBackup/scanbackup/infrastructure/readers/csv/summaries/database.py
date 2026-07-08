import csv
from pathlib import Path
from bson import ObjectId
from scanbackup.shared import DataContentError, FileEmptyError, Configuration
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.summaries.daily import (
    TrafficDailySummaryBBIPField,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.ip.summaries.daily import (
    IPDailySummaryBBIPField,
)
from scanbackup.infrastructure.readers.reader import BaseReader


class TrafficDailySummaryBBIPImport(BaseReader):
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
                row.pop("_id", None)
                try:
                    row[TrafficDailySummaryBBIPField.DEVICE.value] = ObjectId(
                        row[TrafficDailySummaryBBIPField.DEVICE.value]
                    )
                except (ValueError, KeyError):
                    raise DataContentError(extra_msg=f"Valor inválido de id, línea {i}")

                float_fields = [
                    (TrafficDailySummaryBBIPField.IN_MAX, "in max"),
                    (TrafficDailySummaryBBIPField.IN_PROM, "in prom"),
                    (TrafficDailySummaryBBIPField.OUT_MAX, "out max"),
                    (TrafficDailySummaryBBIPField.OUT_PROM, "out prom"),
                    (TrafficDailySummaryBBIPField.USE, "uso"),
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


class IPDailySummaryBBIPImport(BaseReader):
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
                row.pop("_id", None)
                try:
                    row[IPDailySummaryBBIPField.DEVICE.value] = ObjectId(
                        row[IPDailySummaryBBIPField.DEVICE.value]
                    )
                except (ValueError, KeyError):
                    raise DataContentError(extra_msg=f"Valor inválido de id, línea {i}")

                float_fields = [
                    (IPDailySummaryBBIPField.IN_MAX, "in max"),
                    (IPDailySummaryBBIPField.IN_PROM, "in prom"),
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
