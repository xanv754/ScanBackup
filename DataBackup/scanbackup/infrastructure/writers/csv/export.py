import csv
from collections.abc import Sequence
from scanbackup.infrastructure.writers.writer import BaseWriter
from scanbackup.shared import CSVExportError, Configuration
from pydantic import BaseModel


class CSVWriter(BaseWriter):
    def export(
        self,
        filename: str,
        data: Sequence[BaseModel],
        model: type[BaseModel],
        exclude: set | None = None,
    ) -> str:
        filepath = self.dir / filename
        filepath = filepath.with_suffix(".csv")

        try:
            system = Configuration()
            cfg_metadata = system.get_cfg_metadata()
            delimiter = cfg_metadata.scanner.file_delimiter

            if not exclude:
                rows = [item.model_dump(by_alias=True) for item in data]
            else:
                rows = [item.model_dump(by_alias=True, exclude=exclude) for item in data]
            headers = [
                field.alias or name
                for name, field in model.model_fields.items()
                if not exclude or name not in exclude
            ]

            with filepath.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(rows)
        except Exception as error:
            raise CSVExportError(filename=filepath.name, error=error)
        else:
            return str(filepath.resolve())
