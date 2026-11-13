import logging
import re
from collections.abc import Iterator
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import pytest

from interface_sync.utils.logger import ServiceLogger

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"


def line_pattern(level: str, content: str) -> str:
    return f"{DATE_PATTERN} {level} {content}$"


@pytest.fixture
def log_file_path(tmp_path: Path) -> Path:
    return tmp_path / "logs" / "interface-sync.log"


@pytest.fixture
def service_logger(log_file_path: Path, request: pytest.FixtureRequest) -> Iterator[ServiceLogger]:
    logger_name = f"test_{request.node.name}"
    service_logger = ServiceLogger(log_file_path, logger_name=logger_name)
    yield service_logger
    underlying_logger = logging.getLogger(logger_name)
    for handler in list(underlying_logger.handlers):
        handler.close()
        underlying_logger.removeHandler(handler)


def read_lines(log_file_path: Path) -> list[str]:
    return log_file_path.read_text(encoding="utf-8").splitlines()


def test_info_line_has_date_level_message_and_details(
    service_logger: ServiceLogger, log_file_path: Path
) -> None:
    """RF-014: each message has date, level and description."""
    service_logger.info("Registro de nueva interfaz", "'CHC-BRAS-01' ha sido registrado")

    pattern = line_pattern(
        "INFO",
        re.escape("Registro de nueva interfaz - 'CHC-BRAS-01' ha sido registrado"),
    )
    assert re.match(pattern, read_lines(log_file_path)[0])


def test_warning_line_uses_warning_level(
    service_logger: ServiceLogger, log_file_path: Path
) -> None:
    """RF-014: warning level is supported."""
    service_logger.warning("Interfaz incompleta", "'PTF-BORDE-01' sin URL")

    assert re.match(line_pattern("WARNING", ".+"), read_lines(log_file_path)[0])


def test_error_line_uses_error_level(service_logger: ServiceLogger, log_file_path: Path) -> None:
    """RF-014: error level is supported."""
    service_logger.error("Configuración del sistema", "No se ha encontrado la clave `layer`.")

    assert re.match(line_pattern("ERROR", ".+"), read_lines(log_file_path)[0])


def test_message_without_details_omits_separator(
    service_logger: ServiceLogger, log_file_path: Path
) -> None:
    """RF-014: details are optional."""
    service_logger.info("Resultado general exitoso")

    assert read_lines(log_file_path)[0].endswith("INFO Resultado general exitoso")


def test_messages_are_appended_in_order(service_logger: ServiceLogger, log_file_path: Path) -> None:
    """RF-014: log file is written in append mode."""
    service_logger.info("Primero")
    service_logger.info("Segundo")

    lines = read_lines(log_file_path)
    assert lines[0].endswith("Primero")
    assert lines[1].endswith("Segundo")


def test_existing_log_content_is_preserved_on_new_instance(log_file_path: Path) -> None:
    """RF-014: a new run appends to the existing log file."""
    names = ["test_append_first", "test_append_second"]
    try:
        ServiceLogger(log_file_path, logger_name=names[0]).info("Ejecución 1")
        ServiceLogger(log_file_path, logger_name=names[1]).info("Ejecución 2")
    finally:
        for name in names:
            for handler in list(logging.getLogger(name).handlers):
                handler.close()
                logging.getLogger(name).removeHandler(handler)

    assert len(read_lines(log_file_path)) == 2


def test_log_directory_is_created_when_missing(
    service_logger: ServiceLogger, log_file_path: Path
) -> None:
    """RF-014: missing log directory does not prevent logging."""
    assert log_file_path.parent.is_dir()


def test_logger_does_not_propagate_to_root(service_logger: ServiceLogger) -> None:
    """RF-014: the root logger must not be used."""
    assert logging.getLogger("test_test_logger_does_not_propagate_to_root").propagate is False


def test_same_logger_name_does_not_duplicate_handlers(
    service_logger: ServiceLogger, log_file_path: Path
) -> None:
    """RF-014: repeated instantiation must not duplicate log lines."""
    ServiceLogger(log_file_path, logger_name="test_same_logger_name_does_not_duplicate_handlers")
    service_logger.info("Una sola vez")

    assert len(read_lines(log_file_path)) == 1


def test_rotation_is_weekly_and_happens_on_sunday_midnight(
    service_logger: ServiceLogger,
) -> None:
    """RF-014: a log week starts on Sunday and ends on Saturday."""
    handler = logging.getLogger(
        "test_test_rotation_is_weekly_and_happens_on_sunday_midnight"
    ).handlers[0]
    next_rollover = datetime.fromtimestamp(handler.rolloverAt)  # type: ignore

    assert isinstance(handler, TimedRotatingFileHandler)
    assert next_rollover.weekday() == 6
    assert (next_rollover.hour, next_rollover.minute, next_rollover.second) == (0, 0, 0)


def test_rotated_files_are_limited_by_retained_weeks(log_file_path: Path) -> None:
    """RF-014: old log files do not accumulate indefinitely."""
    name = "test_retained_weeks"
    try:
        ServiceLogger(log_file_path, logger_name=name, retained_weeks=3)
        handler = logging.getLogger(name).handlers[0]
        assert handler.backupCount == 3  # type: ignore
    finally:
        for handler in list(logging.getLogger(name).handlers):
            handler.close()
            logging.getLogger(name).removeHandler(handler)
