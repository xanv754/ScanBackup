from typing import TextIO

from reports.reporting.events import (
    Event,
    EventSink,
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
)


class TerminalReporter(EventSink):
    """Shows the progress and the result of the run in the terminal [RF-046].

    Progress and successes go to the output stream; errors, warnings and failed results go to
    the error stream. Interfaces are not printed one by one: the layer line counts them.
    """

    def __init__(self, output: TextIO, errors: TextIO) -> None:
        """Receive the streams to write to."""
        self._output = output
        self._errors = errors

    def publish(self, event: Event) -> None:
        match event:
            case RunStarted():
                date_range = event.date_range
                print(
                    f"Reporte del {date_range.start_key} al {date_range.end_key} "
                    f"({date_range.day_count} días)",
                    file=self._output,
                )
            case ProcessFailed():
                for cause in event.causes:
                    print(f"Error general: {cause}", file=self._errors)
            case LayerEmpty():
                print(f"Capa {event.layer}: sin datos en el rango", file=self._errors)
            case LayerFailed():
                print(f"Capa {event.layer} fallida: {event.cause}", file=self._errors)
            case LayerIncomplete():
                print(
                    f"Capa {event.layer}: {event.interface_count} interfaces con menos "
                    f"resúmenes que los días del rango",
                    file=self._errors,
                )
            case LayerFinished():
                result = event.result
                print(
                    f"Capa {result.layer} {'fallida' if result.failed else 'exitosa'}: "
                    f"{result.included_count} interfaces incluidas",
                    file=self._errors if result.failed else self._output,
                )
            case MissingDay():
                print(f"Día del rango sin resúmenes: {event.day}", file=self._errors)
            case FileGenerated():
                summary = event.summary
                print(
                    f"Archivo generado: {summary.path.name} en {summary.path.parent} "
                    f"({summary.sheet_count} hojas, {summary.interface_count} interfaces)",
                    file=self._output,
                )
            case ExportFailed():
                print(f"Falla al generar el archivo: {event.cause}", file=self._errors)
            case RunFinished():
                result = event.result
                if result.failed:
                    failed_layers = ", ".join(result.failed_layers) or "ninguna"
                    print(
                        f"Resultado general: fallido (capas fallidas: {failed_layers})",
                        file=self._errors,
                    )
                else:
                    print("Resultado general: exitoso", file=self._output)
