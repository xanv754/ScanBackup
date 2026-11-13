from pathlib import Path

from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.cell.cell import Cell
from openpyxl.styles import Font
from openpyxl.worksheet._write_only import WriteOnlyWorksheet

from reports.constants.constants import (
    EXCEL_EXTENSION,
    FORBIDDEN_SHEET_NAME_CHARACTERS,
    FREEZE_PANES_CELL,
    MAX_SHEET_NAME_LENGTH,
    NUMBER_FORMAT,
    SHEET_HEADERS,
)
from reports.domain.models import InterfaceRow, LayerData
from reports.exceptions import ExportError, InvalidSheetNameError
from reports.export.atomic_writer import AtomicFileWriter
from reports.export.exporter import ReportExporter

HEADER_FONT = Font(bold=True)


class XlsxReportExporter(ReportExporter):
    """`ReportExporter` that writes an `.xlsx` file with `openpyxl` in write-only mode.

    The write-only mode streams every sheet to disk, so the memory does not grow with the
    number of interfaces. An instance builds one workbook and is used for a single file.

    A sheet has bold headers in row 1, is frozen at `A2` and has one row per interface.
    Traffic, capacity and usage are numeric cells shown with two decimals; the stored value
    keeps its full precision [RF-040, RF-041]. A layer name is a valid sheet name if it is not
    empty, has at most 31 characters and none of `: \\ / ? * [ ]` [RF-043].
    """

    def __init__(self, writer: AtomicFileWriter | None = None) -> None:
        """Create the empty workbook; `writer` is injected to write the file atomically."""
        self._workbook = Workbook(write_only=True)
        self._writer = writer or AtomicFileWriter()
        self._sheet_count = 0

    @property
    def file_extension(self) -> str:
        return EXCEL_EXTENSION

    def validate_layer_name(self, layer_name: str) -> None:
        if not layer_name:
            raise InvalidSheetNameError("el nombre de la capa está vacío")
        if len(layer_name) > MAX_SHEET_NAME_LENGTH:
            raise InvalidSheetNameError(
                f"el nombre de la capa supera {MAX_SHEET_NAME_LENGTH} caracteres"
            )
        if any(
            character in FORBIDDEN_SHEET_NAME_CHARACTERS for character in layer_name
        ):
            raise InvalidSheetNameError(
                f"el nombre de la capa contiene caracteres no permitidos "
                f"({FORBIDDEN_SHEET_NAME_CHARACTERS})"
            )

    def add_layer(self, data: LayerData) -> None:
        sheet = self._workbook.create_sheet(title=data.layer)
        sheet.freeze_panes = FREEZE_PANES_CELL
        sheet.append(self._header_cells(sheet))
        for row in data.rows:
            sheet.append(self._row_cells(sheet, row))
        self._sheet_count += 1

    def save(self, destination: Path) -> None:
        if self._sheet_count == 0:
            raise ExportError("no hay hojas para escribir")
        try:
            self._writer.write(destination, self._workbook.save)
        finally:
            self._workbook.close()

    @staticmethod
    def _header_cells(sheet: WriteOnlyWorksheet) -> list[Cell]:
        """Return the header cells in bold."""
        cells = []
        for header in SHEET_HEADERS:
            cell = WriteOnlyCell(sheet, value=header)
            cell.font = HEADER_FONT
            cells.append(cell)
        return cells

    @staticmethod
    def _row_cells(sheet: WriteOnlyWorksheet, row: InterfaceRow) -> list[Cell | str]:
        """Return the cells of an interface in the order of the headers."""
        values = (
            row.in_average_gbps,
            row.in_max_gbps,
            row.out_average_gbps,
            row.out_max_gbps,
            row.capacity_gbps,
            row.vendor,
            row.usage_percent,
        )
        cells: list[Cell | str] = [row.name]
        for value in values:
            cell = WriteOnlyCell(sheet, value=value)
            cell.number_format = NUMBER_FORMAT
            cells.append(cell)
        return cells
