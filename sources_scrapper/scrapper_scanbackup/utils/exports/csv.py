import csv
from scrapper_scanbackup.model import SourceModel
from scrapper_scanbackup.utils.exports.base import Exporter


class CSVExporter(Exporter):
    def export(self, data: list[SourceModel]) -> None:
        if not data:
            return

        fieldnames = list(type(data[0]).model_fields.keys())

        filepath = self.filepath.with_suffix(".csv")

        with filepath.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file, fieldnames=fieldnames, delimiter=self.delimiter
            )
            writer.writeheader()
            for item in data:
                writer.writerow(item.model_dump())
