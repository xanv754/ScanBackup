import csv
from pydantic import BaseModel
from scrapper_scanbackup.utils.exports.base import Exporter


class CSVExporter(Exporter):
    def export(self, data: list[BaseModel]) -> None:
        if not data:
            return

        fieldnames = list(type(data[0]).model_fields.keys())

        filepath = self.filepath.with_suffix(".csv")

        with filepath.open("w", newline="", encoding="utf-8") as file:
            file.write(f"{self.header_text}\n")

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                delimiter=self.delimiter,
                lineterminator="\n",
            )
            for item in data:
                writer.writerow(item.model_dump())
