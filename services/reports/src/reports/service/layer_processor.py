from reports.domain.date_range import DateRange
from reports.domain.layers import Layer
from reports.domain.models import LayerData
from reports.domain.period_calculator import PeriodCalculator
from reports.domain.results import LayerOutcome, LayerResult
from reports.exceptions import DatabaseError, InvalidSheetNameError
from reports.export import ReportExporter
from reports.persistence import DailySummaryRepository, InterfaceRepository
from reports.reporting import (
    EventSink,
    LayerEmpty,
    LayerFailed,
    LayerFinished,
    LayerIncomplete,
)

DATABASE_FAILURE_CAUSE = "error de base de datos"


class LayerProcessor:
    """Reads and calculates one layer at a time [RF-034 to RF-038, RF-043].

    The sheet name is validated before any data is read. Layer membership and the descriptive
    data come from `interfaces`; the summaries are aggregated by the database. Interfaces
    without summaries in the range are not included. A failure of the layer is reported and
    returned as a failed result, never raised, so the next layer can be processed.
    """

    def __init__(
        self,
        interface_repository: InterfaceRepository,
        summary_repository: DailySummaryRepository,
        calculator: PeriodCalculator,
        exporter: ReportExporter,
        event_sink: EventSink,
    ) -> None:
        """Receive the collaborators; the exporter is only used to validate the sheet name."""
        self._interfaces = interface_repository
        self._summaries = summary_repository
        self._calculator = calculator
        self._exporter = exporter
        self._event_sink = event_sink

    def process(self, layer: Layer, date_range: DateRange) -> LayerOutcome:
        """Return the result of the layer and, if it has interfaces, the rows to export."""
        try:
            self._exporter.validate_layer_name(layer.name)
        except InvalidSheetNameError as error:
            return self._fail(layer.name, f"nombre de capa inválido como hoja: {error}")
        try:
            outcome = self._read(layer, date_range)
        except DatabaseError as error:
            return self._fail(layer.name, f"{DATABASE_FAILURE_CAUSE} ({error})")
        result = outcome.result
        if not result.has_data:
            self._event_sink.publish(LayerEmpty(layer.name))
        if result.incomplete_count > 0:
            self._event_sink.publish(
                LayerIncomplete(layer.name, result.incomplete_count)
            )
        self._event_sink.publish(LayerFinished(result))
        return outcome

    def _read(self, layer: Layer, date_range: DateRange) -> LayerOutcome:
        """Read, aggregate and calculate the layer. Raises `DatabaseError` on a database error."""
        interfaces = {
            interface.id: interface
            for interface in self._interfaces.find_by_layer_values(layer.stored_values)
        }
        interface_ids = list(interfaces)
        summaries = self._summaries.aggregate(interface_ids, date_range)
        dates_with_summary = frozenset(
            self._summaries.dates_with_summary(interface_ids, date_range)
        )
        rows = sorted(
            (
                self._calculator.calculate(interfaces[summary.interface_id], summary)
                for summary in summaries
            ),
            key=lambda row: row.sort_key,
        )
        result = LayerResult(
            layer=layer.name,
            included_count=len(rows),
            incomplete_count=sum(
                1 for summary in summaries if summary.days < date_range.day_count
            ),
            dates_with_summary=dates_with_summary,
        )
        data = LayerData(layer=layer.name, rows=tuple(rows)) if rows else None
        return LayerOutcome(result=result, data=data)

    def _fail(self, layer_name: str, cause: str) -> LayerOutcome:
        """Report the failure of a layer and return its failed result."""
        result = LayerResult(layer=layer_name, failure_cause=cause)
        self._event_sink.publish(LayerFailed(layer_name, cause))
        self._event_sink.publish(LayerFinished(result))
        return LayerOutcome(result=result)
