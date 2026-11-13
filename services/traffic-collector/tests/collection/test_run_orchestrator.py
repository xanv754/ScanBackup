from datetime import date

import pytest

from tests.collection.fakes import FakeInterfaceReader, RecordingSink, make_interface
from traffic_collector.clock import TargetDate
from traffic_collector.collection import RunOrchestrator
from traffic_collector.constants.enums import CutReason, ExitCode
from traffic_collector.domain.results import LayerResult, RunResult, SummaryResult
from traffic_collector.exceptions import ProcessError
from traffic_collector.reporting.events import LayerFinished, RunFinished

TARGET = TargetDate.previous_day(date(2026, 11, 6))

OK = LayerResult(layer="", active_count=3, stored_count=3)
SKIPPED = LayerResult(layer="", active_count=3, skipped_count=3)
EMPTY = LayerResult(layer="")
FAILED = LayerResult(layer="", active_count=3, stored_count=2, failed_count=1)
CUT = LayerResult(
    layer="", active_count=5, failed_count=3, cut_reason=CutReason.CONSECUTIVE_FAILURES
)
UNREADABLE = LayerResult(layer="", read_failed=True)


class FakeLayerCollector:
    """LayerCollector that returns a preset result per layer and records the order."""

    def __init__(self, results: dict[str, LayerResult]) -> None:
        self._results = results
        self.processed: list[str] = []
        self.summary_calls_at_processing: list[int] = []

    def process(self, layer: str) -> LayerResult:
        self.processed.append(layer)
        preset = self._results[layer]
        return LayerResult(
            layer=layer,
            active_count=preset.active_count,
            skipped_count=preset.skipped_count,
            stored_count=preset.stored_count,
            failed_count=preset.failed_count,
            cut_reason=preset.cut_reason,
            read_failed=preset.read_failed,
        )


class FakeSummaryPhase:
    """SummaryPhase that records how many layers were processed when it ran."""

    def __init__(self, collector: FakeLayerCollector, failed_count: int = 0) -> None:
        self._collector = collector
        self._failed_count = failed_count
        self.layers_processed_before_run: list[int] = []

    def run(self, target_date: TargetDate) -> SummaryResult:
        self.layers_processed_before_run.append(len(self._collector.processed))
        return SummaryResult(failed_count=self._failed_count)


def build(results: dict[str, LayerResult], summary_failed_count: int = 0) -> tuple[
    RunOrchestrator,
    FakeLayerCollector,
    FakeSummaryPhase,
    RecordingSink,
    FakeInterfaceReader,
]:
    collector = FakeLayerCollector(results)
    summary = FakeSummaryPhase(collector, summary_failed_count)
    sink = RecordingSink()
    reader = FakeInterfaceReader({layer: [make_interface()] for layer in results})
    orchestrator = RunOrchestrator(TARGET, reader, collector, summary, sink)
    return orchestrator, collector, summary, sink, reader


def test_layers_are_processed_in_ascending_order_then_summary_once() -> None:
    """Layers run one after another in order and the summary runs once at the end (RF-019)."""
    orchestrator, collector, summary, _, _ = build(
        {"DIST": OK, "BORDE": OK, "BRAS": OK}
    )

    orchestrator.run()

    assert collector.processed == ["BORDE", "BRAS", "DIST"]
    assert summary.layers_processed_before_run == [3]


def test_failed_layer_does_not_stop_the_next_ones() -> None:
    """A failed or cut layer never prevents the following layers (RF-019, RF-027)."""
    orchestrator, collector, summary, _, _ = build({"A": CUT, "B": OK, "C": FAILED})

    result = orchestrator.run()

    assert collector.processed == ["A", "B", "C"]
    assert summary.layers_processed_before_run == [3]
    assert result.failed


def test_no_layers_is_a_process_error_without_processing() -> None:
    """Without layers the process fails before any SCAN request (RF-018, RF-028)."""
    orchestrator, collector, summary, _, _ = build({})

    with pytest.raises(ProcessError):
        orchestrator.run()

    assert collector.processed == []
    assert summary.layers_processed_before_run == []


def test_database_down_is_a_process_error_without_processing() -> None:
    """If the database is down the process fails before any SCAN request (RF-018, RF-028)."""
    orchestrator, collector, summary, _, reader = build({"A": OK})
    reader.fail_layers = True

    with pytest.raises(ProcessError):
        orchestrator.run()

    assert collector.processed == []
    assert summary.layers_processed_before_run == []


def test_summary_runs_even_if_every_layer_failed() -> None:
    """The summary phase runs after the layers even if they failed (RF-026)."""
    orchestrator, _, summary, _, _ = build({"A": CUT, "B": UNREADABLE})

    orchestrator.run()

    assert summary.layers_processed_before_run == [2]


def test_events_report_each_layer_and_the_final_result() -> None:
    """Every layer and the final result are published as events (RF-030)."""
    orchestrator, _, _, sink, _ = build({"A": OK, "B": FAILED})

    result = orchestrator.run()

    assert [event.result.layer for event in sink.of_type(LayerFinished)] == ["A", "B"]
    assert sink.of_type(RunFinished)[0].result is result


def layers_of(*layers: LayerResult, summary_failed_count: int = 0) -> RunResult:
    return RunResult(
        layers=tuple(layers), summary=SummaryResult(failed_count=summary_failed_count)
    )


def test_all_layers_successful_is_a_successful_run() -> None:
    """Every layer successful gives exit code 0 (RF-028)."""
    assert layers_of(OK, OK).exit_code is ExitCode.SUCCESS


def test_rerun_with_everything_skipped_is_successful() -> None:
    """A rerun where all interfaces are skipped exits with 0 (RF-020, RF-028)."""
    assert layers_of(SKIPPED, SKIPPED).exit_code is ExitCode.SUCCESS


def test_empty_layers_are_ignored_when_another_has_interfaces() -> None:
    """An empty layer does not fail the run if another layer has interfaces (RF-019, RF-028)."""
    assert layers_of(EMPTY, OK).exit_code is ExitCode.SUCCESS


def test_all_layers_empty_is_a_failed_run() -> None:
    """If no layer has active interfaces the exit code is not zero (RF-019, RF-028)."""
    assert layers_of(EMPTY, EMPTY).exit_code is ExitCode.FAILED


@pytest.mark.parametrize(
    "bad_layer", [FAILED, CUT, UNREADABLE], ids=["failed", "cut", "unread"]
)
def test_any_failed_layer_makes_the_run_failed(bad_layer: LayerResult) -> None:
    """One failed, cut or unreadable layer fails the run (RF-028)."""
    assert layers_of(OK, bad_layer).exit_code is ExitCode.FAILED


def test_failed_summary_makes_the_run_failed() -> None:
    """A failed summary fails the run (RF-026, RF-028)."""
    assert layers_of(OK, summary_failed_count=1).exit_code is ExitCode.FAILED
