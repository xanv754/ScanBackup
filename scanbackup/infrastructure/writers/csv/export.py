import csv
from scanbackup.infrastructure.writers.writer import BaseWriter
from scanbackup.shared import CSVExportError, Configuration
from pydantic import BaseModel


class CSVWriter(BaseWriter):
    def export(
        self, filename: str, data: list[BaseModel], exclude: set | None = None
    ) -> None:
        filepath = self.dir / filename
        filepath = filepath.with_suffix(".csv")

        try:
            system = Configuration()
            cfg_metadata = system.get_cfg_metadata()
            delimiter = cfg_metadata.scanner.file_delimiter

            if not exclude:
                rows = [item.model_dump() for item in data]
            else:
                rows = [item.model_dump(exclude=exclude) for item in data]
            headers = list(rows[0].keys())

            with filepath.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(rows)
        except Exception as error:
            raise CSVExportError(filename=filepath.name, error=error)
