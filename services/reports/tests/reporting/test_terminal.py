import io

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
    RunStarted,
    TerminalReporter,
)
from tests.reporting.events_samples import (
    DATE_RANGE,
    EXPORT_SUMMARY,
    FAILED_LAYER,
    FAILED_RUN,
    OK_LAYER,
    SUCCESSFUL_RUN,
)


def publish(event: object) -> tuple[str, str]:
    """Publish one event and return what went to the output and to the error stream."""
    output, errors = io.StringIO(), io.StringIO()
    TerminalReporter(output, errors).publish(event)
    return output.getvalue(), errors.getvalue()


@pytest.mark.parametrize(
    ("event", "text"),
    [
        (RunStarted(DATE_RANGE), "Reporte del 2026-03-01 al 2026-03-31 (31 días)"),
        (LayerFinished(OK_LAYER), "Capa BORDE exitosa: 4 interfaces incluidas"),
        (FileGenerated(EXPORT_SUMMARY), "Archivo generado: ScanBackup_x.xlsx en /exports"),
        (RunFinished(SUCCESSFUL_RUN), "Resultado general: exitoso"),
    ],
)
def test_rf046_progress_and_successes_go_to_the_output(event: object, text: str) -> None:
    """RF-046: range, layer result, generated file and general result are shown."""
    output, errors = publish(event)
    assert text in output
    assert errors == ""


@pytest.mark.parametrize(
    ("event", "text"),
    [
        (LayerEmpty("BORDE"), "Capa BORDE: sin datos en el rango"),
        (LayerFailed("BRAS", "error de base de datos"), "Capa BRAS fallida: error de base"),
        (LayerIncomplete("BORDE", 3), "3 interfaces con menos resúmenes"),
        (LayerFinished(FAILED_LAYER), "Capa BRAS fallida: 0 interfaces incluidas"),
        (MissingDay("2026-03-05"), "Día del rango sin resúmenes: 2026-03-05"),
        (ExportFailed("disco lleno"), "disco lleno"),
        (ProcessFailed(("causa uno", "causa dos")), "Error general: causa dos"),
        (RunFinished(FAILED_RUN), "Resultado general: fallido (capas fallidas: BRAS)"),
    ],
)
def test_rf046_errors_and_warnings_go_to_the_error_stream(event: object, text: str) -> None:
    """RF-046: warnings, failures and errors with their cause go to stderr."""
    output, errors = publish(event)
    assert text in errors
    assert output == ""
