import csv
from pathlib import Path
from bson import ObjectId
from scanbackup.shared import DataContentError, FileEmptyError
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.data import (
    TrafficBBIPField,
)
from scanbackup.infrastructure.readers.reader import BaseReader


class TrafficHistoryBBIPImport(BaseReader):
    _delimiter: str

    def __init__(self, delimiter: str = ",") -> None:
        self._delimiter = delimiter

    def import_data(self, filepath: Path) -> list[dict]:
        if filepath.stat().st_size == 0:
            raise FileEmptyError(filepath=filepath)

        with filepath.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=self._delimiter)
            rows = []
            for i, row in enumerate(reader, start=1):
                try:
                    row[TrafficBBIPField.DEVICE.value] = ObjectId(
                        row[TrafficBBIPField.DEVICE.value]
                    )
                except (ValueError, KeyError):
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

