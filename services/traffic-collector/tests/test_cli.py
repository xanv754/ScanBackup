import io
import socket
from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner

from traffic_collector.cli import cli, execute
from traffic_collector.constants.enums import ExitCode

TODAY = date(2026, 11, 6)
VALID_CONFIG = "max_concurrent_requests: 5\nrequest_timeout_seconds: 30\nmax_consecutive_failures: 5\n"


@pytest.fixture
def environment(tmp_path: Path) -> dict[str, str]:
    config_path = tmp_path / "config.yml"
    config_path.write_text(VALID_CONFIG, encoding="utf-8")
    return {
        "CONFIG_PATH": str(config_path),
        "SCAN_USERNAME": "operator",
        "SCAN_PASSWORD": "s3cr3t-pass",
        "MONGO_HOST": "127.0.0.1",
        "MONGO_PORT": "27017",
        "MONGO_USERNAME": "root",
        "MONGO_PASSWORD": "mongo-s3cr3t",
        "MONGO_DATABASE": "scan_backup",
    }


def run_execute(
    environment: dict[str, str], log_path: Path
) -> tuple[ExitCode, str, str]:
    output, errors = io.StringIO(), io.StringIO()
    exit_code = execute(False, environment, TODAY, log_path, output, errors)
    return exit_code, output.getvalue(), errors.getvalue()


def test_invalid_settings_exit_with_process_error_and_are_logged(
    environment: dict[str, str], tmp_path: Path
) -> None:
    """Invalid configuration is a general error, reported in log and stderr (RF-028)."""
    del environment["SCAN_PASSWORD"]
    log_path = tmp_path / "logs" / "traffic-collector.log"

    exit_code, _, errors = run_execute(environment, log_path)

    assert exit_code is ExitCode.PROCESS_ERROR
    assert "SCAN_PASSWORD" not in errors
    assert "password" in errors
    assert "password" in log_path.read_text(encoding="utf-8")


def test_secrets_never_reach_log_or_terminal(
    environment: dict[str, str], tmp_path: Path
) -> None:
    """Passwords do not appear in log or terminal even when startup fails (RF-029)."""
    environment["MONGO_PORT"] = "not-a-port"
    log_path = tmp_path / "traffic-collector.log"

    _, output, errors = run_execute(environment, log_path)

    combined = output + errors + log_path.read_text(encoding="utf-8")
    assert "s3cr3t-pass" not in combined
    assert "mongo-s3cr3t" not in combined


def test_unwritable_log_is_a_process_error(
    environment: dict[str, str], tmp_path: Path
) -> None:
    """If the log file cannot be written the process fails with code 2 (RF-029)."""
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")

    exit_code, _, errors = run_execute(environment, blocker / "traffic-collector.log")

    assert exit_code is ExitCode.PROCESS_ERROR
    assert "log" in errors


def test_database_down_is_a_process_error(
    environment: dict[str, str], tmp_path: Path
) -> None:
    """An unreachable database is a general error before any SCAN request (RF-018, RF-028)."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        environment["MONGO_PORT"] = str(probe.getsockname()[1])
    log_path = tmp_path / "traffic-collector.log"

    exit_code, _, errors = run_execute(environment, log_path)

    assert exit_code is ExitCode.PROCESS_ERROR
    assert "Base de datos no disponible" in errors


def test_help_documents_force_and_exit_codes() -> None:
    """The command exposes --force and documents the exit codes (RF-017)."""
    result = CliRunner().invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "--force" in result.output
    assert "Códigos de salida" in result.output
