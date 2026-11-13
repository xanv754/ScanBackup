from datetime import datetime
from pathlib import Path

from reports.constants.constants import CARACAS_TIMEZONE
from reports.export import ReportFileNamer
from reports.report_config import ReportConfig

GENERATED_AT = datetime(2026, 11, 10, 15, 30, 0, tzinfo=CARACAS_TIMEZONE)


def namer(
    prefix_name: str = "ScanBackup", date_format: str = "%Y%m%d_%H%M%S"
) -> ReportFileNamer:
    """Build a namer with the given configuration."""
    return ReportFileNamer(ReportConfig(prefix_name, date_format, Path("/exports")))


def test_rf042_default_name() -> None:
    """RF-042: with the defaults the name is ScanBackup_20261110_153000.xlsx."""
    assert namer().file_name(GENERATED_AT, ".xlsx") == "ScanBackup_20261110_153000.xlsx"


def test_rf042_custom_prefix_and_format() -> None:
    """RF-042: the prefix and the date format come from the configuration."""
    assert (
        namer("Weekly", "%Y-%m-%d").file_name(GENERATED_AT, ".xlsx")
        == "Weekly_2026-11-10.xlsx"
    )


def test_rf042_format_without_directives_always_gives_the_same_name() -> None:
    """RF-042: a format without directives keeps the name constant (it overwrites)."""
    assert (
        namer(date_format="latest").file_name(GENERATED_AT, ".xlsx")
        == "ScanBackup_latest.xlsx"
    )
