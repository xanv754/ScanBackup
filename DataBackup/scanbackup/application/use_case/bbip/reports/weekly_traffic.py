from pathlib import Path
from datetime import date, timedelta
from scanbackup.domain import (
    TrafficSourceBBIPRepository,
    TrafficDailySummaryBBIPRepository,
    TrafficReportBBIPExporter,
    TrafficReportService,
)
from scanbackup.shared import ExportError, ExcelExportError


class TrafficWeeklyReportGeneratorUseCase:
    """Generates the weekly traffic report of every active interface, grouped by layer, into a single .xlsx file."""

    _repo_sources: TrafficSourceBBIPRepository
    _repo_daily: TrafficDailySummaryBBIPRepository
    _report_exporter: TrafficReportBBIPExporter
    _layers: list[str]
    _start_date: date
    _end_date: date
    _filename: str
    _output_dir: Path | None

    def __init__(
        self,
        source_repository: TrafficSourceBBIPRepository,
        daily_repository: TrafficDailySummaryBBIPRepository,
        report_exporter: TrafficReportBBIPExporter,
        layers: list[str],
        reference_date: date,
        filename: str,
        literal: bool = False,
        output_dir: Path | None = None,
    ) -> None:
        """Store the collaborators used to read the stored data and export the resulting report.

        Args:
            source_repository (TrafficSourceBBIPRepository): Repository queried
                for every active interface's descriptive data.
            daily_repository (TrafficDailySummaryBBIPRepository): Repository
                queried for the stored daily summaries within the target week.
            report_exporter (TrafficReportBBIPExporter): Exporter used to
                write the joined rows into the resulting report file.
            layers (list[str]): Every configured traffic layer, in any casing.
                One Excel sheet is produced per layer, even when it has no data.
            reference_date (date): The day the report is generated for. The
                target week is computed from this date.
            filename (str): Base name of the .xlsx file to create, without extension.
            literal (bool): When False (default), the week runs from the Monday
                of the week before `reference_date`'s week (Sunday-first) through
                that week's Sunday. When True, the week is the 7 trailing days
                counting back from `reference_date`, inclusive.
            output_dir (Path | None): Directory where the resulting .xlsx file
                is written. Defaults to the writer's built-in directory when omitted.
        """
        self._repo_sources = source_repository
        self._repo_daily = daily_repository
        self._report_exporter = report_exporter
        self._layers = layers
        self._start_date, self._end_date = self.resolve_week_range(
            reference_date, literal
        )
        self._filename = filename
        self._output_dir = output_dir

    @staticmethod
    def resolve_week_range(reference_date: date, literal: bool) -> tuple[date, date]:
        """Resolve the (start_date, end_date) of the target week for `reference_date`.

        In literal mode, the week is the 7 trailing days counting back from
        `reference_date`, inclusive. Otherwise, weeks start on Sunday: the
        week is the Monday of the week before `reference_date`'s week through
        that week's Sunday.
        """
        if literal:
            return reference_date - timedelta(days=6), reference_date

        days_since_sunday = (reference_date.weekday() + 1) % 7
        current_week_sunday = reference_date - timedelta(days=days_since_sunday)
        return current_week_sunday - timedelta(days=6), current_week_sunday

    def execute(self) -> str:
        """Generate the weekly traffic report of every active interface, grouped by layer.

        Reads every active source (regardless of layer) and every stored
        daily summary within the target week, rolls each device's daily
        summaries into a single weekly aggregate, joins the result with its
        source, and exports one Excel sheet per configured layer, created
        even when a layer has no data for the week.

        Returns:
            str: The absolute path of the generated .xlsx file.
        """
        try:
            sources = self._repo_sources.get_all_active_sources()
            summaries = self._repo_daily.get_by_date_range(
                self._start_date, self._end_date
            )
            weekly_summaries = TrafficReportService.aggregate_by_device(
                summaries, self._start_date
            )
            rows = TrafficReportService.build_rows(sources, weekly_summaries)
            return self._report_exporter.export(
                rows, self._layers, self._filename, self._output_dir
            )
        except ExcelExportError:
            raise
        except Exception as error:
            raise ExportError(
                message="Error al generar el reporte semanal de tráfico",
                error=error,
            )
