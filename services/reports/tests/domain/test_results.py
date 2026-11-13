from pathlib import Path

from reports.constants.enums import ExitCode
from reports.domain.results import ExportSummary, LayerResult, RunResult

WRITTEN = ExportSummary(path=Path("/exports/a.xlsx"), sheet_count=1, interface_count=3)


def ok_layer(layer: str = "BORDE", included: int = 3) -> LayerResult:
    """Build a successful layer with `included` interfaces."""
    return LayerResult(layer=layer, included_count=included)


def failed_layer(layer: str = "BRAS") -> LayerResult:
    """Build a failed layer."""
    return LayerResult(layer=layer, failure_cause="error de base de datos")


def test_rf044_all_layers_ok_and_file_written_is_success() -> None:
    """RF-044: everything succeeded: exit code 0."""
    result = RunResult((ok_layer(), ok_layer("BRAS")), export_summary=WRITTEN)
    assert result.exit_code == ExitCode.SUCCESS


def test_rf044_layer_without_data_does_not_fail_if_another_has_data() -> None:
    """RF-044: a successful layer without data still gives a successful run."""
    result = RunResult(
        (ok_layer(), ok_layer("BRAS", included=0)), export_summary=WRITTEN
    )
    assert result.exit_code == ExitCode.SUCCESS


def test_rf044_failed_layer_fails_the_run_but_keeps_the_file() -> None:
    """RF-044: a failed layer gives exit code 1 even if the others were exported."""
    result = RunResult((ok_layer(), failed_layer()), export_summary=WRITTEN)
    assert result.failed_layers == ("BRAS",)
    assert result.exit_code == ExitCode.FAILED


def test_rf044_no_layer_with_data_fails_the_run() -> None:
    """RF-044: no layer contributed data, so there is no file and the run is failed."""
    result = RunResult((ok_layer(included=0), ok_layer("BRAS", included=0)))
    assert result.exit_code == ExitCode.FAILED


def test_rf044_write_failure_fails_the_run() -> None:
    """RF-044: a failure writing the file gives exit code 1."""
    result = RunResult((ok_layer(),), export_failed=True)
    assert result.exit_code == ExitCode.FAILED
