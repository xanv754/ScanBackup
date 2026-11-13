from datetime import date
from pathlib import Path

from reports.domain.date_range import DateRange
from reports.domain.results import ExportSummary, LayerResult, RunResult

DATE_RANGE = DateRange(start=date(2026, 3, 1), end=date(2026, 3, 31))
EXPORT_SUMMARY = ExportSummary(
    path=Path("/exports/ScanBackup_x.xlsx"), sheet_count=2, interface_count=7
)
OK_LAYER = LayerResult(layer="BORDE", included_count=4)
FAILED_LAYER = LayerResult(layer="BRAS", failure_cause="error de base de datos")
SUCCESSFUL_RUN = RunResult((OK_LAYER,), export_summary=EXPORT_SUMMARY)
FAILED_RUN = RunResult((OK_LAYER, FAILED_LAYER), export_summary=EXPORT_SUMMARY)
