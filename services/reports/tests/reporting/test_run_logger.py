import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from reports.reporting import (
    ExportFailed,
    FileGenerated,
    LayerEmpty,
    LayerFailed,
    LayerFinished,
    LayerIncomplete,
    MissingDay,
    ProcessFailed,
    RunFinished,
    RunLogger,
    RunStarted,
    create_file_logger,
)
from tests.reporting.events_samples import (
    DATE_RANGE,
    EXPORT_SUMMARY,
    FAILED_LAYER,
    FAILED_RUN,
    OK_LAYER,
    SUCCESSFUL_RUN,
)


@pytest.fixture
def log_path(tmp_path: Path) -> Iterator[Path]:
    """A log file path; the service logger is released afterwards."""
    yield tmp_path / "logs" / "reports.log"
    for handler in list(logging.getLogger("reports").handlers):
        handler.close()
        logging.getLogger("reports").removeHandler(handler)


def log_lines(log_path: Path, *events: object) -> list[str]:
    """Publish `events` through a `RunLogger` and return the lines written to the file."""
    run_logger = RunLogger(create_file_logger(log_path))
    for event in events:
        run_logger.publish(event)
    run_logger.close()
    return log_path.read_text(encoding="utf-8").splitlines()


@pytest.mark.parametrize(
    ("event", "level", "text"),
    [
        (RunStarted(DATE_RANGE), "INFO", "2026-03-01 a 2026-03-31"),
        (LayerEmpty("BORDE"), "WARNING", "BORDE"),
        (
            LayerFailed("BRAS", "error de base de datos"),
            "ERROR",
            "BRAS fallida: error de base",
        ),
        (MissingDay("2026-03-05"), "WARNING", "2026-03-05"),
        (LayerIncomplete("BORDE", 3), "WARNING", "BORDE: 3 interfaces"),
        (LayerFinished(OK_LAYER), "INFO", "BORDE exitosa: 4 interfaces incluidas"),
        (LayerFinished(FAILED_LAYER), "ERROR", "BRAS fallida: 0 interfaces incluidas"),
        (
            FileGenerated(EXPORT_SUMMARY),
            "INFO",
            "ScanBackup_x.xlsx en /exports (2 hojas, 7 inter",
        ),
        (ExportFailed("disco lleno"), "ERROR", "disco lleno"),
        (RunFinished(SUCCESSFUL_RUN), "INFO", "exitoso"),
        (RunFinished(FAILED_RUN), "ERROR", "fallido (capas fallidas: BRAS)"),
    ],
)
def test_rf045_each_event_is_logged_with_level_and_content(
    log_path: Path, event: object, level: str, text: str
) -> None:
    """RF-045: every event of the table has its level and its content."""
    (line,) = log_lines(log_path, event)
    assert f" {level} " in line
    assert text in line


def test_rf045_one_error_entry_per_cause(log_path: Path) -> None:
    """RF-045: each invalid parameter or config cause is its own Error entry."""
    lines = log_lines(log_path, ProcessFailed(("causa uno", "causa dos")))
    assert len(lines) == 2
    assert all(" ERROR " in line for line in lines)
    assert "causa uno" in lines[0]
    assert "causa dos" in lines[1]


def test_rf045_each_line_has_date_time_level_and_description(log_path: Path) -> None:
    """RF-045: the line starts with a timestamp followed by the level and the text."""
    (line,) = log_lines(log_path, LayerEmpty("BORDE"))
    assert line[:4].isdigit()
    assert line[4] == "-"
    assert ":" in line[:19]
    assert " WARNING Capa BORDE" in line


def test_rf045_messages_of_previous_runs_are_kept(log_path: Path) -> None:
    """RF-045: the file is appended to, not truncated, on the next run."""
    log_lines(log_path, LayerEmpty("PRIMERA"))
    lines = log_lines(log_path, LayerEmpty("SEGUNDA"))
    assert len(lines) == 2
    assert "PRIMERA" in lines[0]
    assert "SEGUNDA" in lines[1]


def test_rf045_log_directory_is_created_if_missing(log_path: Path) -> None:
    """RF-045: the directory of the log file is created when it does not exist."""
    assert not log_path.parent.exists()
    log_lines(log_path, LayerEmpty("BORDE"))
    assert log_path.exists()
