import gc
from pathlib import Path

import pytest
from openpyxl import Workbook, load_workbook

from reports.domain.models import InterfaceRow, LayerData
from reports.exceptions import ExportError, InvalidSheetNameError
from reports.export import XlsxReportExporter

HEADERS = ["Interfaz", "In Prom", "In Max", "Out Prom", "Out Max", "Capacidad", "Tipo", "Uso (%)"]


def row(name: str = "ETH-1", vendor: str = "HUAWEI", **values: float) -> InterfaceRow:
    """Build a report row; every traffic value is 1.0 unless overridden."""
    defaults = {
        "in_average_gbps": 1.0,
        "in_max_gbps": 2.0,
        "out_average_gbps": 3.0,
        "out_max_gbps": 4.0,
        "capacity_gbps": 10.0,
        "usage_percent": 40.0,
    }
    return InterfaceRow(name=name, vendor=vendor, scan_url=f"url/{name}", **{**defaults, **values})


def write_file(destination: Path, layers: list[LayerData]) -> None:
    """Export `layers`, in order, to `destination`."""
    exporter = XlsxReportExporter()
    for layer in layers:
        exporter.add_layer(layer)
    exporter.save(destination)


def test_rf039_one_sheet_per_layer_in_the_order_added(tmp_path: Path) -> None:
    """RF-039: sheets are named after the layer, in order, and there are no extra sheets."""
    destination = tmp_path / "report.xlsx"
    write_file(
        destination,
        [LayerData("BORDE", (row(),)), LayerData("IXP", (row(),)), LayerData("ALFA", (row(),))],
    )
    assert load_workbook(destination).sheetnames == ["BORDE", "IXP", "ALFA"]


def test_rf040_headers_are_exact_and_in_row_one(tmp_path: Path) -> None:
    """RF-040: row 1 has the eight headers in the exact order."""
    destination = tmp_path / "report.xlsx"
    write_file(destination, [LayerData("BORDE", (row(),))])
    sheet = load_workbook(destination)["BORDE"]
    assert [cell.value for cell in sheet[1]] == HEADERS


def test_rf040_columns_follow_the_specified_order(tmp_path: Path) -> None:
    """RF-040: Interfaz, In Prom, In Max, Out Prom, Out Max, Capacidad, Tipo, Uso (%)."""
    destination = tmp_path / "report.xlsx"
    write_file(destination, [LayerData("BORDE", (row("ETH-9", "JUNIPER"),))])
    sheet = load_workbook(destination)["BORDE"]
    assert [cell.value for cell in sheet[2]] == ["ETH-9", 1.0, 2.0, 3.0, 4.0, 10.0, "JUNIPER", 40.0]


def test_rf040_numeric_values_are_numeric_cells_and_keep_precision(tmp_path: Path) -> None:
    """RF-040, RF-041: numbers are not text and the stored value is not rounded."""
    destination = tmp_path / "report.xlsx"
    precise = row(in_average_gbps=1.23456789012, capacity_gbps=0.0, usage_percent=0.0)
    write_file(destination, [LayerData("BORDE", (precise,))])
    sheet = load_workbook(destination)["BORDE"]
    for column in "BCDEFH":
        assert isinstance(sheet[f"{column}2"].value, int | float)
    assert sheet["B2"].value == 1.23456789012
    assert sheet["F2"].value == 0


def test_rf040_rows_are_written_in_the_given_order(tmp_path: Path) -> None:
    """RF-040: the exporter keeps the order of the rows it receives."""
    destination = tmp_path / "report.xlsx"
    write_file(destination, [LayerData("BORDE", (row("A"), row("B"), row("C")))])
    sheet = load_workbook(destination)["BORDE"]
    assert [sheet[f"A{number}"].value for number in (2, 3, 4)] == ["A", "B", "C"]


def test_rf041_header_is_bold_and_first_row_is_frozen(tmp_path: Path) -> None:
    """RF-041: bold header row and frozen first row (A2)."""
    destination = tmp_path / "report.xlsx"
    write_file(destination, [LayerData("BORDE", (row(),))])
    sheet = load_workbook(destination)["BORDE"]
    assert all(cell.font.b for cell in sheet[1])
    assert not sheet["A2"].font.b
    assert sheet.freeze_panes == "A2"


def test_rf041_columns_b_to_h_use_two_decimals(tmp_path: Path) -> None:
    """RF-041: number format `0.00` in columns B to H."""
    destination = tmp_path / "report.xlsx"
    write_file(destination, [LayerData("BORDE", (row(),))])
    sheet = load_workbook(destination)["BORDE"]
    assert [sheet[f"{column}2"].number_format for column in "BCDEFGH"] == ["0.00"] * 7


def test_rf042_file_is_overwritten_when_it_exists(tmp_path: Path) -> None:
    """RF-042: a file with the same name is replaced."""
    destination = tmp_path / "report.xlsx"
    write_file(destination, [LayerData("OLD", (row(),))])
    write_file(destination, [LayerData("NEW", (row(),))])
    assert load_workbook(destination).sheetnames == ["NEW"]


def test_rf042_no_sheets_writes_no_file(tmp_path: Path) -> None:
    """RF-042: without sheets there is no file."""
    destination = tmp_path / "report.xlsx"
    with pytest.raises(ExportError):
        XlsxReportExporter().save(destination)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
def test_rf042_failed_write_leaves_no_partial_file_and_keeps_the_previous_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RF-042: if writing fails the temporary file is removed and the old file is intact."""
    destination = tmp_path / "report.xlsx"
    write_file(destination, [LayerData("OLD", (row(),))])
    previous_content = destination.read_bytes()

    def fail_after_partial_write(self: Workbook, filename: Path) -> None:
        Path(filename).write_bytes(b"partial")
        raise OSError("disk full")

    monkeypatch.setattr(Workbook, "save", fail_after_partial_write)
    exporter = XlsxReportExporter()
    exporter.add_layer(LayerData("NEW", (row(),)))
    with pytest.raises(ExportError, match="disk full"):
        exporter.save(destination)
    gc.collect()
    assert destination.read_bytes() == previous_content
    assert [path.name for path in tmp_path.iterdir()] == ["report.xlsx"]


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
def test_rf042_failed_write_without_previous_file_leaves_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RF-042: a failed first write leaves no file at all."""
    monkeypatch.setattr(Workbook, "save", lambda self, filename: Path(filename).write_bytes(b"x"))
    monkeypatch.setattr(Path, "replace", lambda self, target: (_ for _ in ()).throw(OSError("no")))
    exporter = XlsxReportExporter()
    exporter.add_layer(LayerData("NEW", (row(),)))
    with pytest.raises(ExportError):
        exporter.save(tmp_path / "report.xlsx")
    gc.collect()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("name", ["BORDE", "A" * 31, "CAPA_1", "CAPA 1"])
def test_rf043_valid_sheet_names(name: str) -> None:
    """RF-043: up to 31 characters without forbidden characters are valid."""
    XlsxReportExporter().validate_layer_name(name)


@pytest.mark.parametrize("name", ["", "A" * 32, "A:B", "A\\B", "A/B", "A?B", "A*B", "A[B", "A]B"])
def test_rf043_invalid_sheet_names(name: str) -> None:
    """RF-043: empty, longer than 31 or with `: \\ / ? * [ ]` are invalid sheet names."""
    with pytest.raises(InvalidSheetNameError):
        XlsxReportExporter().validate_layer_name(name)
