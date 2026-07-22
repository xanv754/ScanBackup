from pathlib import Path
from calendar import monthrange
from datetime import date, timedelta
from scanbackup.domain import (
    TrafficSourceBBIPRepository,
    TrafficDailySummaryBBIPRepository,
    TrafficReportBBIPExporter,
    TrafficReportService,
)
from scanbackup.shared import ExportError, ExcelExportError


class TrafficMonthlyReportGeneratorUseCase:
    """Generates the monthly traffic report of every active interface, grouped by layer, into a single .xlsx file."""

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
        filename: str,
        year: int | None = None,
        month: int | None = None,
        literal: bool = False,
        reference_date: date | None = None,
        output_dir: Path | None = None,
    ) -> None:
        """Store the collaborators used to read the stored data and export the resulting report.

        Args:
            source_repository (TrafficSourceBBIPRepository): Repository queried
                for every active interface's descriptive data.
            daily_repository (TrafficDailySummaryBBIPRepository): Repository
                queried for the stored daily summaries within the target period.
            report_exporter (TrafficReportBBIPExporter): Exporter used to
                write the joined rows into the resulting report file.
            layers (list[str]): Every configured traffic layer, in any casing.
                One Excel sheet is produced per layer, even when it has no data.
            filename (str): Base name of the .xlsx file to create, without extension.
            year (int | None): Year of the target month. Required when literal is False.
            month (int | None): Month to report, from 1 to 12. Required when literal is False.
            literal (bool): When False (default), the period runs from the
                1st through the last day of `year`/`month`. When True, the
                period is the 30 trailing days counting back from
                `reference_date`, inclusive.
            reference_date (date | None): The day the report is generated for.
                Required when literal is True.
            output_dir (Path | None): Directory where the resulting .xlsx file
                is written. Defaults to the writer's built-in directory when omitted.
        """
        self._repo_sources = source_repository
        self._repo_daily = daily_repository
        self._report_exporter = report_exporter
        self._layers = layers
        if literal:
            self._start_date, self._end_date = self.resolve_literal_range(
                reference_date
            )
        else:
            self._start_date = date(year, month, 1)
            self._end_date = date(year, month, monthrange(year, month)[1])
        self._filename = filename
        self._output_dir = output_dir

    @staticmethod
    def resolve_literal_range(reference_date: date) -> tuple[date, date]:
        """Resolve the (start_date, end_date) of the 30 trailing days counting back from `reference_date`, inclusive."""
        return reference_date - timedelta(days=29), reference_date

    def execute(self) -> str:
        """Generate the monthly traffic report of every active interface, grouped by layer.

        Reads every active source (regardless of layer) and every stored
        daily summary within the target month, rolls each device's daily
        summaries into a single monthly aggregate, joins the result with its
        source, and exports one Excel sheet per configured layer, created
        even when a layer has no data for the month.

        Returns:
            str: The absolute path of the generated .xlsx file.
        """
        try:
            sources = self._repo_sources.get_all_active_sources()
            summaries = self._repo_daily.get_by_date_range(
                self._start_date, self._end_date
            )
            monthly_summaries = TrafficReportService.aggregate_by_device(
                summaries, self._start_date
            )
            rows = TrafficReportService.build_rows(sources, monthly_summaries)
            return self._report_exporter.export(
                rows, self._layers, self._filename, self._output_dir
            )
        except ExcelExportError:
            raise
        except Exception as error:
            raise ExportError(
                message="Error al generar el reporte mensual de tráfico",
                error=error,
            )
