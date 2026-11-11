from pathlib import Path

from reports.clock import Clock
from reports.constants.constants import LAYERS_READ_ERROR_CAUSE, NO_LAYERS_CAUSE
from reports.domain.date_range import DateRange
from reports.domain.layers import Layer, LayerCatalog
from reports.domain.results import ExportSummary, LayerResult, RunResult
from reports.exceptions import DatabaseError, ExportError, ProcessError
from reports.export import ReportExporter, ReportFileNamer
from reports.persistence import InterfaceRepository
from reports.reporting import (
    EventSink,
    ExportFailed,
    FileGenerated,
    MissingDay,
    RunFinished,
    RunStarted,
)
from reports.service.layer_processor import LayerProcessor


class ReportService:
    """Orchestrates the generation of the report [RF-031, RF-044].

    It obtains the existing layers, processes them one by one in report order, adds a sheet for
    each layer with data, evaluates the days without summaries and writes the file if there is
    at least one sheet. It depends only on abstractions: it knows neither click nor the file
    format. A general error of the process is raised as `ProcessError` before any layer is read.
    """

    def __init__(
        self,
        interface_repository: InterfaceRepository,
        layer_processor: LayerProcessor,
        exporter: ReportExporter,
        file_namer: ReportFileNamer,
        export_directory: Path,
        clock: Clock,
        event_sink: EventSink,
    ) -> None:
        """Receive the collaborators injected by the composition root."""
        self._interfaces = interface_repository
        self._layer_processor = layer_processor
        self._exporter = exporter
        self._file_namer = file_namer
        self._export_directory = export_directory
        self._clock = clock
        self._event_sink = event_sink

    def run(self, date_range: DateRange) -> RunResult:
        """Generate the report of the range and return the overall result.

        Raises `ProcessError` if the layers cannot be obtained or no layer exists.
        """
        layers = self._existing_layers()
        self._event_sink.publish(RunStarted(date_range))
        layer_results: list[LayerResult] = []
        sheet_count = 0
        interface_count = 0
        for layer in layers:
            outcome = self._layer_processor.process(layer, date_range)
            layer_results.append(outcome.result)
            if outcome.data is not None:
                self._exporter.add_layer(outcome.data)
                sheet_count += 1
                interface_count += outcome.result.included_count
        missing_days = self._missing_days(layer_results, date_range)
        for day in missing_days:
            self._event_sink.publish(MissingDay(day))
        export_summary, export_failed = self._export(sheet_count, interface_count)
        result = RunResult(
            layer_results=tuple(layer_results),
            missing_days=missing_days,
            export_summary=export_summary,
            export_failed=export_failed,
        )
        self._event_sink.publish(RunFinished(result))
        return result

    def _existing_layers(self) -> tuple[Layer, ...]:
        """Return the existing layers in report order or raise `ProcessError`."""
        try:
            stored_values = self._interfaces.layer_values()
        except DatabaseError as error:
            raise ProcessError([f"{LAYERS_READ_ERROR_CAUSE} ({error})"]) from error
        layers = LayerCatalog(stored_values).ordered()
        if not layers:
            raise ProcessError([NO_LAYERS_CAUSE])
        return layers

    @staticmethod
    def _missing_days(layer_results: list[LayerResult], date_range: DateRange) -> tuple[str, ...]:
        """Return the days without summaries in every successfully processed layer [RF-036].

        Nothing is evaluated when no layer succeeded: its days were not read, not missing.
        """
        successful = [result for result in layer_results if not result.failed]
        if not successful:
            return ()
        days_with_summary = frozenset().union(*(result.dates_with_summary for result in successful))
        return tuple(day for day in date_range.day_keys() if day not in days_with_summary)

    def _export(self, sheet_count: int, interface_count: int) -> tuple[ExportSummary | None, bool]:
        """Write the file if there is a sheet; return its summary and whether writing failed."""
        if sheet_count == 0:
            return None, False
        file_name = self._file_namer.file_name(self._clock.now(), self._exporter.file_extension)
        destination = self._export_directory / file_name
        try:
            self._exporter.save(destination)
        except ExportError as error:
            self._event_sink.publish(ExportFailed(str(error)))
            return None, True
        summary = ExportSummary(
            path=destination, sheet_count=sheet_count, interface_count=interface_count
        )
        self._event_sink.publish(FileGenerated(summary))
        return summary, False
