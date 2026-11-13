import io
import os
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner
from openpyxl import load_workbook
from pymongo.database import Database

from reports import cli as cli_module
from reports.cli import cli, execute
from reports.constants.enums import ExitCode
from reports.exceptions import DatabaseError
from tests.conftest import MONGO_ENVIRONMENT
from tests.fakes import FixedClock

PASSWORD = MONGO_ENVIRONMENT["MONGO_PASSWORD"]


class Execution:
    """What a run of `execute` produced."""

    def __init__(self, code: ExitCode, output: str, errors: str, log: str) -> None:
        """Keep the exit code, both terminal streams and the log text."""
        self.code = code
        self.output = output
        self.errors = errors
        self.log = log


@pytest.fixture
def valid_config(tmp_path: Path, export_directory: Path) -> Path:
    """A valid config file whose export directory exists."""
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        f'metadata:\n  reports:\n    export_path: "{export_directory}"\n',
        encoding="utf-8",
    )
    return config_path


@pytest.fixture
def run(tmp_path: Path, clock: FixedClock) -> Callable[..., Execution]:
    """Return a function that runs `execute` with captured streams and a temporary log."""

    def run_execute(
        start: str | None,
        end: str | None,
        environment: dict[str, str],
        extras: tuple[str, ...] = (),
        log_path: Path | None = None,
    ) -> Execution:
        log_file = log_path or tmp_path / "logs" / "reports.log"
        output, errors = io.StringIO(), io.StringIO()
        code = execute(start, end, extras, environment, clock, log_file, output, errors)
        log = log_file.read_text(encoding="utf-8") if log_file.exists() else ""
        return Execution(code, output.getvalue(), errors.getvalue(), log)

    return run_execute


class ForbiddenConnection:
    """A connection that must never be created."""

    def __init__(self, *_: object) -> None:
        """Fail the test as soon as it is built."""
        pytest.fail(
            "MongoDB must not be opened when parameters or configuration are invalid"
        )


def test_rf031_invalid_parameters_and_config_are_accumulated_without_opening_mongo(
    run: Callable[..., Execution], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RF-031, RF-033, RF-032: causes of both validations are reported together; no connection."""
    monkeypatch.setattr(cli_module, "MongoConnection", ForbiddenConnection)
    config_path = tmp_path / "bad.yml"
    config_path.write_text(
        'metadata:\n  reports:\n    prefix_name: ""\n', encoding="utf-8"
    )
    environment = {**MONGO_ENVIRONMENT, "CONFIG_PATH": str(config_path)}
    execution = run("2026-1-5", None, environment, extras=("--layer",))
    assert execution.code == ExitCode.PROCESS_ERROR
    for cause in (
        "--start debe tener el formato",
        "Falta la opción --end",
        "--layer",
        "prefix_name",
    ):
        assert cause in execution.errors
        assert cause in execution.log
    assert execution.log.count(" ERROR ") == 4
    assert "Reporte del" not in execution.output
    assert "Inicio de la ejecución" not in execution.log


def test_rf032_missing_config_file_is_a_general_error(
    run: Callable[..., Execution],
) -> None:
    """RF-032: a config file that does not exist is a general error (exit 2)."""
    environment = {**MONGO_ENVIRONMENT, "CONFIG_PATH": "/does/not/exist.yml"}
    execution = run("2026-03-01", "2026-03-02", environment)
    assert execution.code == ExitCode.PROCESS_ERROR
    assert "No se puede leer" in execution.errors


def test_rf044_database_unavailable_is_a_general_error_and_secrets_are_not_shown(
    run: Callable[..., Execution], valid_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RF-044: unavailable database gives exit 2, closes the connection and hides the password."""
    closed: list[bool] = []

    class UnavailableConnection:
        def __init__(self, *_: object) -> None:
            pass

        def verify(self) -> None:
            raise DatabaseError("ServerSelectionTimeoutError")

        def close(self) -> None:
            closed.append(True)

    monkeypatch.setattr(cli_module, "MongoConnection", UnavailableConnection)
    environment = {**MONGO_ENVIRONMENT, "CONFIG_PATH": str(valid_config)}
    execution = run("2026-03-01", "2026-03-02", environment)
    assert execution.code == ExitCode.PROCESS_ERROR
    assert "Base de datos no disponible" in execution.errors
    assert "Base de datos no disponible" in execution.log
    assert closed == [True]
    assert PASSWORD not in execution.errors + execution.log + execution.output


def test_rf044_unexpected_error_is_a_general_error(
    run: Callable[..., Execution], valid_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RF-044: an unexpected exception is reported and gives exit 2."""

    class BrokenConnection:
        def __init__(self, *_: object) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(cli_module, "MongoConnection", BrokenConnection)
    environment = {**MONGO_ENVIRONMENT, "CONFIG_PATH": str(valid_config)}
    execution = run("2026-03-01", "2026-03-02", environment)
    assert execution.code == ExitCode.PROCESS_ERROR
    assert "Error inesperado: RuntimeError: boom" in execution.errors


def test_rf045_unwritable_log_is_a_general_error_shown_in_the_terminal(
    run: Callable[..., Execution], valid_config: Path, tmp_path: Path
) -> None:
    """RF-045: if the log file cannot be written the run stops with exit 2."""
    blocker = tmp_path / "blocker"
    blocker.write_text("file", encoding="utf-8")
    environment = {**MONGO_ENVIRONMENT, "CONFIG_PATH": str(valid_config)}
    execution = run(
        "2026-03-01", "2026-03-02", environment, log_path=blocker / "reports.log"
    )
    assert execution.code == ExitCode.PROCESS_ERROR
    assert "No se puede escribir el archivo de log" in execution.errors


def test_rf031_help_describes_the_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """RF-031: --help describes --start, --end, the format, inclusive ends and the end limit."""
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    for text in (
        "--start",
        "--end",
        "YYYY-MM-DD",
        "incluido",
        "anterior al día actual",
    ):
        assert text in result.output
    assert "0  resultado general exitoso" in result.output


def test_rf033_cli_reports_unrecognized_options_and_missing_values(
    tmp_path: Path, valid_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RF-033: click does not abort by itself: unknown options and missing options are causes."""
    monkeypatch.setattr(cli_module, "LOG_DIRECTORY", str(tmp_path / "logs"))
    monkeypatch.setattr(cli_module, "MongoConnection", ForbiddenConnection)
    monkeypatch.setenv("CONFIG_PATH", str(valid_config))
    for name, value in MONGO_ENVIRONMENT.items():
        monkeypatch.setenv(name, value)
    result = CliRunner().invoke(cli, ["--unknown", "x"])
    assert result.exit_code == ExitCode.PROCESS_ERROR
    log_text = (tmp_path / "logs" / "reports.log").read_text(encoding="utf-8")
    assert "Falta la opción --start" in log_text
    assert "Falta la opción --end" in log_text
    assert "Opción no reconocida: --unknown" in log_text


def seed(
    database: Database, layer: str, name: str, vendor: str, capacity: float
) -> None:
    """Insert an interface with three daily summaries (March 1 to 3)."""
    interface_id = (
        database["interfaces"]
        .insert_one(
            {
                "layer": layer,
                "name": name,
                "vendor": vendor,
                "capacity_gbps": capacity,
                "scan_url": f"url/{layer}/{name}",
                "status": "activa",
            }
        )
        .inserted_id
    )
    for day, in_avg, in_max in (("2026-03-01", 2e9, 5e9), ("2026-03-02", 4e9, 9e9)):
        database["traffic_summary_daily"].insert_one(
            {
                "interface_id": interface_id,
                "layer": layer,
                "date": day,
                "in_avg": in_avg,
                "out_avg": 1e9,
                "in_max": in_max,
                "out_max": 3e9,
            }
        )


def integration_environment(database: Database, config_path: Path) -> dict[str, str]:
    """Build the environment pointing to the throwaway database."""
    return {
        "MONGO_HOST": os.environ["MONGO_HOST"],
        "MONGO_PORT": os.environ.get("MONGO_PORT", "27017"),
        "MONGO_USERNAME": os.environ["MONGO_USERNAME"],
        "MONGO_PASSWORD": os.environ["MONGO_PASSWORD"],
        "MONGO_AUTH_SOURCE": os.environ.get("MONGO_AUTH_SOURCE", "admin"),
        "MONGO_DATABASE": database.name,
        "CONFIG_PATH": str(config_path),
    }


@pytest.mark.integration
def test_rf031_full_run_writes_the_report_with_the_calculated_values(
    run: Callable[..., Execution],
    database: Database,
    valid_config: Path,
    export_directory: Path,
) -> None:
    """RF-031, RF-035, RF-038, RF-042: a real run exports one sheet per layer with the values."""
    seed(database, "BRAS", "ae1", "huawei", 10)
    seed(database, "borde", "eth-1", "", 0)
    execution = run(
        "2026-03-01", "2026-03-03", integration_environment(database, valid_config)
    )
    assert execution.code == ExitCode.SUCCESS
    (report,) = export_directory.glob("ScanBackup_*.xlsx")
    workbook = load_workbook(report)
    assert workbook.sheetnames == ["BORDE", "BRAS"]
    assert [cell.value for cell in workbook["BRAS"][2]] == [
        "AE1",
        3.0,
        9.0,
        1.0,
        3.0,
        10,
        "HUAWEI",
        90.0,
    ]
    assert [cell.value for cell in workbook["BORDE"][2]][-2:] == ["UNDEFINED", 0]
    assert "Archivo generado" in execution.output
    assert "Día del rango sin resúmenes: 2026-03-03" in execution.errors
    assert "AE1" not in execution.log + execution.output
    assert "eth-1" not in execution.log + execution.output
    assert execution.log.count("Capa BRAS exitosa") == 1


@pytest.mark.integration
def test_rf044_layer_with_invalid_sheet_name_fails_but_the_rest_is_exported(
    run: Callable[..., Execution],
    database: Database,
    valid_config: Path,
    export_directory: Path,
) -> None:
    """RF-043, RF-044: a layer with forbidden characters fails; the rest is still exported."""
    seed(database, "BORDE", "eth-1", "huawei", 10)
    seed(database, "BAD/LAYER", "eth-2", "huawei", 10)
    execution = run(
        "2026-03-01", "2026-03-02", integration_environment(database, valid_config)
    )
    assert execution.code == ExitCode.FAILED
    (report,) = export_directory.glob("ScanBackup_*.xlsx")
    assert load_workbook(report).sheetnames == ["BORDE"]
    assert "Capa BAD/LAYER fallida" in execution.errors
    assert "Resultado general: fallido (capas fallidas: BAD/LAYER)" in execution.errors


@pytest.mark.integration
def test_rf044_range_without_data_writes_no_file_and_fails(
    run: Callable[..., Execution],
    database: Database,
    valid_config: Path,
    export_directory: Path,
) -> None:
    """RF-044: layers exist but none has summaries in the range: no file, exit 1."""
    seed(database, "BORDE", "eth-1", "huawei", 10)
    execution = run(
        "2025-01-01", "2025-01-02", integration_environment(database, valid_config)
    )
    assert execution.code == ExitCode.FAILED
    assert list(export_directory.iterdir()) == []
    assert "Capa BORDE: sin datos en el rango" in execution.errors


@pytest.mark.integration
def test_rf044_database_without_layers_is_a_general_error(
    run: Callable[..., Execution], database: Database, valid_config: Path
) -> None:
    """RF-044: no layer in the database gives exit 2 and no file."""
    execution = run(
        "2026-03-01", "2026-03-02", integration_environment(database, valid_config)
    )
    assert execution.code == ExitCode.PROCESS_ERROR
    assert "No hay capas en la base de datos" in execution.errors


@pytest.mark.integration
def test_rf031_two_runs_give_the_same_content(
    run: Callable[..., Execution],
    database: Database,
    valid_config: Path,
    export_directory: Path,
) -> None:
    """RF-031: running the same range twice produces the same sheet contents."""
    seed(database, "BORDE", "eth-1", "huawei", 10)
    seed(database, "BORDE", "eth-2", "zte", 40)
    environment = integration_environment(database, valid_config)

    def contents() -> list[list[object]]:
        run("2026-03-01", "2026-03-02", environment)
        report = max(export_directory.glob("ScanBackup_*.xlsx"))
        return [
            [cell.value for cell in row]
            for row in load_workbook(report)["BORDE"].iter_rows()
        ]

    assert contents() == contents()
