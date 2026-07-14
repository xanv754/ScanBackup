from collections import defaultdict
from pandas import DataFrame, ExcelWriter as PandasExcelWriter
from pydantic import BaseModel
from scanbackup.infrastructure.writers.writer import BaseWriter
from scanbackup.shared import ExcelExportError


class ExcelWriter(BaseWriter):
    def export(
        self,
        filename: str,
        data: list[BaseModel],
        model: type[BaseModel],
        sheet_field: str,
        sheet_names: list[str],
        exclude: set | None = None,
    ) -> str:
        """Export the given entities into a multi-sheet .xlsx file, one sheet per name in `sheet_names`.

        Entities are grouped by the value of their `sheet_field` attribute. A
        sheet is created for every name in `sheet_names`, even when no
        entities belong to it, using `model`'s fields as the header row.

        Args:
            filename (str): Base name of the file to create, without extension.
            data (list[BaseModel]): The entities to export, of type `model`.
            model (type[BaseModel]): The entity type, used to derive column
                headers even for sheets with no rows.
            sheet_field (str): Name of the attribute used to group entities
                into sheets.
            sheet_names (list[str]): Every sheet to create, in order.
            exclude (set | None): Field names to omit from the headers and rows.

        Returns:
            str: The absolute path of the generated .xlsx file.
        """
        filepath = self.dir / filename
        filepath = filepath.with_suffix(".xlsx")

        try:
            grouped: dict[str, list[BaseModel]] = defaultdict(list)
            for item in data:
                grouped[getattr(item, sheet_field)].append(item)

            headers = [
                field
                for field in model.model_fields
                if not exclude or field not in exclude
            ]

            with PandasExcelWriter(filepath, engine="openpyxl") as excel:
                for sheet_name in sheet_names:
                    rows = grouped.get(sheet_name, [])
                    records = [row.model_dump(exclude=exclude) for row in rows]
                    dataframe = DataFrame(records, columns=headers)
                    dataframe.to_excel(excel, sheet_name=sheet_name, index=False)
        except Exception as error:
            raise ExcelExportError(filename=filepath.name, error=error)
        else:
            return str(filepath.resolve())
