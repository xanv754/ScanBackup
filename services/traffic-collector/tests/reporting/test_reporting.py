import io
import logging
from collections.abc import Iterator
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pytest

from tests.collection.fakes import RecordingSink, make_interface
from traffic_collector.constants.enums import CutReason, FailureCause, SampleCountVerdict
from traffic_collector.domain.results import LayerResult, RunResult, SummaryResult
from traffic_collector.exceptions import DatabaseError
from traffic_collector.reporting import (
    CompositeEventSink,
    InterfaceFailed,
    InterfaceInvalidLines,
    InterfaceSampleCountWarning,
    LayerCut,
    LayerEmpty,
    LayerFinished,
    LayerReadFailed,
    LayerStarted,
    RunFinished,
    RunLogger,
    SummaryFailed,
    SummaryFinished,
    TerminalReporter,
    create_file_logger,
)

OK_LAYER = LayerResult(layer="BORDE", active_count=3, stored_count=3)
FAILED_LAYER = LayerResult(layer="DIST", active_count=3, stored_count=2, failed_count=1)


@pytest.fixture
def log_path(tmp_path: Path) -> Iterator[Path]:
    yield tmp_path / "logs" / "traffic-collector.log"
    logging.getLogger("traffic_collector").handlers.clear()


def read_log(run_logger: RunLogger, log_path: Path) -> str:
    run_logger.close()
    return log_path.read_text(encoding="utf-8")


def test_file_logger_creates_a_rotating_file_and_its_directory(log_path: Path) -> None:
    """The log is a rotating file created with its directory (RF-029)."""
    logger = create_file_logger(log_path)

    assert log_path.parent.is_dir()
    assert any(isinstance(handler, RotatingFileHandler) for handler in logger.handlers)
    assert not logger.propagate


def test_creating_the_logger_twice_does_not_duplicate_lines(log_path: Path) -> None:
    """A second call replaces the handler instead of adding another one (RF-029)."""
    create_file_logger(log_path)
    run_logger = RunLogger(create_file_logger(log_path))

    run_logger.publish(LayerEmpty("BORDE"))

    assert read_log(run_logger, log_path).count("sin interfaces activas") == 1


def test_log_writes_levels_layer_interface_and_cause(log_path: Path) -> None:
    """Errors and warnings include layer, interface and cause (RF-029)."""
    run_logger = RunLogger(create_file_logger(log_path))
    interface = make_interface("https://scan/a.log")

    run_logger.publish(LayerEmpty("BRAS"))
    run_logger.publish(InterfaceFailed("BORDE", interface, FailureCause.TIMEOUT))
    run_logger.publish(
        InterfaceSampleCountWarning("BORDE", interface, SampleCountVerdict.PARTIAL, 200)
    )
    run_logger.publish(InterfaceInvalidLines("BORDE", interface, 2))
    run_logger.publish(LayerCut("BORDE", CutReason.CONSECUTIVE_FAILURES, 7))
    run_logger.publish(LayerReadFailed("DIST"))
    content = read_log(run_logger, log_path)

    assert "WARNING Capa BRAS: sin interfaces activas" in content
    assert "ERROR Capa BORDE: interfaz" in content
    assert "https://scan/a.log" in content
    assert "tiempo de espera agotado" in content
    assert "almacenada con 200 muestras" in content
    assert "2 líneas inválidas" in content
    assert "cortado por fallas consecutivas; 7 interfaces sin procesar" in content
    assert "ERROR Capa DIST" in content


def test_log_marks_failed_layers_and_runs_as_errors(log_path: Path) -> None:
    """A failed layer and a failed run are logged as errors, successful ones as info (RF-029)."""
    run_logger = RunLogger(create_file_logger(log_path))

    run_logger.publish(LayerFinished(OK_LAYER))
    run_logger.publish(LayerFinished(FAILED_LAYER))
    run_logger.publish(SummaryFinished(generated_count=2, skipped_count=1))
    run_logger.publish(SummaryFailed(generated_count=2, error=DatabaseError("x")))
    run_logger.publish(RunFinished(RunResult((OK_LAYER, FAILED_LAYER), SummaryResult())))
    content = read_log(run_logger, log_path)

    assert "INFO Capa BORDE exitosa" in content
    assert "ERROR Capa DIST fallida" in content
    assert "INFO Resumen diario exitoso: 2 generados, 1 omitidos" in content
    assert "ERROR Resumen diario fallido" in content
    assert "ERROR Resultado general: fallido" in content


def test_log_has_one_line_per_event_and_no_line_per_successful_interface(log_path: Path) -> None:
    """A successful layer produces only its start and finish lines (RF-029)."""
    run_logger = RunLogger(create_file_logger(log_path))

    run_logger.publish(LayerStarted("BORDE", 1000, 0))
    run_logger.publish(LayerFinished(OK_LAYER))

    assert len(read_log(run_logger, log_path).splitlines()) == 2


def test_terminal_sends_errors_to_stderr_and_progress_to_stdout() -> None:
    """Progress goes to stdout and errors to stderr (RF-030)."""
    output, errors = io.StringIO(), io.StringIO()
    terminal = TerminalReporter(output, errors)

    terminal.publish(LayerStarted("BORDE", 10, 2))
    terminal.publish(LayerFinished(OK_LAYER))
    terminal.publish(LayerFinished(FAILED_LAYER))
    terminal.publish(LayerCut("DIST", CutReason.STORAGE_ERROR, 4))
    terminal.publish(LayerReadFailed("IXP"))
    terminal.publish(RunFinished(RunResult((OK_LAYER, FAILED_LAYER), SummaryResult())))

    assert "Capa BORDE: 10 interfaces activas, 2 omitidas" in output.getvalue()
    assert "Capa BORDE exitosa" in output.getvalue()
    assert "Capa DIST fallida" in errors.getvalue()
    assert "cortada por error de base de datos al almacenar" in errors.getvalue()
    assert "Capa IXP" in errors.getvalue()
    assert "Resultado general: fallido" in errors.getvalue()
    assert "Capa DIST" not in output.getvalue()


def test_terminal_reports_success_in_stdout_and_ignores_single_interfaces() -> None:
    """A successful run is reported in stdout; single interface events stay out (RF-030)."""
    output, errors = io.StringIO(), io.StringIO()
    terminal = TerminalReporter(output, errors)

    terminal.publish(InterfaceFailed("BORDE", make_interface(), FailureCause.TIMEOUT))
    terminal.publish(RunFinished(RunResult((OK_LAYER,), SummaryResult())))

    assert "Resultado general: exitoso" in output.getvalue()
    assert errors.getvalue() == ""


def test_composite_delivers_every_event_to_every_sink() -> None:
    """The composite forwards each event to all its sinks in order (RF-029, RF-030)."""
    first, second = RecordingSink(), RecordingSink()

    CompositeEventSink((first, second)).publish(LayerEmpty("BORDE"))

    assert first.events == second.events == [LayerEmpty("BORDE")]
