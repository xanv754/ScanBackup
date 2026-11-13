from traffic_collector.clock import TargetDate
from traffic_collector.collection.protocols import (
    InterfaceReader,
    LayerCollector,
    SummaryPhase,
)
from traffic_collector.constants.constants import (
    DATABASE_UNAVAILABLE_CAUSE,
    NO_LAYERS_CAUSE,
)
from traffic_collector.domain.results import LayerResult, RunResult
from traffic_collector.exceptions import DatabaseError, ProcessError
from traffic_collector.reporting.events import EventSink, LayerFinished, RunFinished


class RunOrchestrator:
    """Runs the whole collection: every layer in order, then the daily summary [RF-018, RF-019].

    A failed or cut layer never stops the next ones, and the summary always runs after them.
    """

    def __init__(
        self,
        target_date: TargetDate,
        interface_reader: InterfaceReader,
        layer_collector: LayerCollector,
        summary_phase: SummaryPhase,
        event_sink: EventSink,
    ) -> None:
        """Receive the day, the collaborators and the sink for the events."""
        self._target_date = target_date
        self._interface_reader = interface_reader
        self._layer_collector = layer_collector
        self._summary_phase = summary_phase
        self._event_sink = event_sink

    def run(self) -> RunResult:
        """Execute the collection and return the overall result [RF-028].

        Raises `ProcessError` before any SCAN request if the database is unavailable or there
        are no layers.
        """
        layers = self._read_layers()
        layer_results: list[LayerResult] = []
        for layer in layers:
            layer_result = self._layer_collector.process(layer)
            self._event_sink.publish(LayerFinished(layer_result))
            layer_results.append(layer_result)
        summary_result = self._summary_phase.run(self._target_date)
        run_result = RunResult(layers=tuple(layer_results), summary=summary_result)
        self._event_sink.publish(RunFinished(run_result))
        return run_result

    def _read_layers(self) -> list[str]:
        """Return the layers in ascending order or raise `ProcessError`."""
        try:
            layers = self._interface_reader.layers()
        except DatabaseError as error:
            raise ProcessError([DATABASE_UNAVAILABLE_CAUSE]) from error
        if not layers:
            raise ProcessError([NO_LAYERS_CAUSE])
        return layers
