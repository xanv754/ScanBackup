from typing import TextIO

from traffic_collector.reporting.events import (
    Event,
    LayerCut,
    LayerEmpty,
    LayerFinished,
    LayerReadFailed,
    LayerStarted,
    ProcessFailed,
    RunFinished,
    SummaryFailed,
    SummaryFinished,
)


class TerminalReporter:
    """Shows the progress and the result of the run in the terminal [RF-030].

    Progress goes to the output stream and errors to the error stream. Failures of single
    interfaces are not printed one by one (they are in the log): the layer line counts them.
    """

    def __init__(self, output: TextIO, errors: TextIO) -> None:
        """Receive the streams to write to."""
        self._output = output
        self._errors = errors

    def publish(self, event: Event) -> None:
        """Print the events that matter to the operator and ignore the rest."""
        match event:
            case LayerStarted():
                print(
                    f"Capa {event.layer}: {event.active_count} interfaces activas, "
                    f"{event.skipped_count} omitidas",
                    file=self._output,
                )
            case LayerEmpty():
                print(f"Capa {event.layer}: sin interfaces activas", file=self._output)
            case LayerReadFailed():
                print(
                    f"Capa {event.layer}: error al leer la base de datos",
                    file=self._errors,
                )
            case LayerCut():
                print(
                    f"Capa {event.layer}: cortada por {event.reason.value} "
                    f"({event.not_processed_count} sin procesar)",
                    file=self._errors,
                )
            case LayerFinished():
                result = event.result
                stream = self._errors if result.failed else self._output
                print(
                    f"Capa {result.layer} {'fallida' if result.failed else 'exitosa'}: "
                    f"{result.stored_count} almacenadas, {result.skipped_count} omitidas, "
                    f"{result.failed_count} fallidas",
                    file=stream,
                )
            case SummaryFinished():
                print(
                    f"Resumen diario exitoso: {event.generated_count} generados, "
                    f"{event.skipped_count} omitidos",
                    file=self._output,
                )
            case SummaryFailed():
                print(
                    f"Resumen diario fallido: error de base de datos "
                    f"({event.generated_count} generados)",
                    file=self._errors,
                )
            case ProcessFailed():
                for cause in event.causes:
                    print(f"Error general: {cause}", file=self._errors)
            case RunFinished():
                failed = event.result.failed
                print(
                    f"Resultado general: {'fallido' if failed else 'exitoso'}",
                    file=self._errors if failed else self._output,
                )
