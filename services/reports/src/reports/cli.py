import os
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import TextIO

import click

from reports.clock import Clock, SystemClock
from reports.constants.constants import (
    DATABASE_UNAVAILABLE_CAUSE,
    LOG_DIRECTORY,
    LOG_FILE_ERROR_CAUSE,
    LOG_FILE_NAME,
    UNEXPECTED_ERROR_CAUSE,
)
from reports.constants.enums import ExitCode
from reports.domain.date_range import DateRangeValidator
from reports.domain.period_calculator import PeriodCalculator
from reports.exceptions import DatabaseError, ProcessError
from reports.export import ReportFileNamer, XlsxReportExporter
from reports.persistence import (
    MongoConnection,
    MongoDailySummaryRepository,
    MongoInterfaceRepository,
)
from reports.reporting import (
    CompositeEventSink,
    EventSink,
    ProcessFailed,
    RunLogger,
    TerminalReporter,
    create_file_logger,
)
from reports.service import LayerProcessor, ReportService
from reports.settings import Settings, SettingsLoader


def execute(
    start: str | None,
    end: str | None,
    extra_arguments: Sequence[str],
    environment: Mapping[str, str],
    clock: Clock,
    log_path: Path,
    output: TextIO,
    errors: TextIO,
) -> ExitCode:
    """Assemble every dependency, generate the report and return the process exit code.

    The parameters and the configuration are both validated and all their causes reported
    together; with any cause no connection to MongoDB is opened. Any error that prevents the
    report returns `ExitCode.PROCESS_ERROR`.
    """
    terminal = TerminalReporter(output, errors)
    try:
        run_logger = RunLogger(create_file_logger(log_path))
    except OSError as error:
        terminal.publish(ProcessFailed((f"{LOG_FILE_ERROR_CAUSE} ({error})",)))
        return ExitCode.PROCESS_ERROR

    event_sink = CompositeEventSink((run_logger, terminal))
    connection: MongoConnection | None = None
    try:
        causes: list[str] = []
        date_range = _collect(
            lambda: DateRangeValidator(clock).validate(start, end, extra_arguments),
            causes,
        )
        settings = _collect(SettingsLoader(environment).load, causes)
        if causes or date_range is None or settings is None:
            raise ProcessError(causes)
        connection = MongoConnection(settings.mongo)
        connection.verify()
        service = _build_service(settings, connection, clock, event_sink)
        return service.run(date_range).exit_code
    except ProcessError as error:
        event_sink.publish(ProcessFailed(tuple(error.causes)))
    except DatabaseError:
        event_sink.publish(ProcessFailed((DATABASE_UNAVAILABLE_CAUSE,)))
    except Exception as error:
        event_sink.publish(
            ProcessFailed(
                (f"{UNEXPECTED_ERROR_CAUSE}: {type(error).__name__}: {error}",)
            )
        )
    finally:
        if connection is not None:
            connection.close()
        run_logger.close()
    return ExitCode.PROCESS_ERROR


def _collect[ValueT](
    validate: Callable[[], ValueT], causes: list[str]
) -> ValueT | None:
    """Run a validation; add its causes to `causes` and return None if it fails."""
    try:
        return validate()
    except ProcessError as error:
        causes.extend(error.causes)
        return None


def _build_service(
    settings: Settings, connection: MongoConnection, clock: Clock, event_sink: EventSink
) -> ReportService:
    """Create the repositories, the exporter and the processor and wire them into the service."""
    database = connection.database
    interface_repository = MongoInterfaceRepository(database)
    exporter = XlsxReportExporter()
    layer_processor = LayerProcessor(
        interface_repository=interface_repository,
        summary_repository=MongoDailySummaryRepository(database),
        calculator=PeriodCalculator(),
        exporter=exporter,
        event_sink=event_sink,
    )
    return ReportService(
        interface_repository=interface_repository,
        layer_processor=layer_processor,
        exporter=exporter,
        file_namer=ReportFileNamer(settings.report),
        export_directory=settings.report.export_path,
        clock=clock,
        event_sink=event_sink,
    )


@click.command(
    name="reports",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.option(
    "--start",
    type=str,
    default=None,
    help="Primer día del rango, en formato YYYY-MM-DD (incluido). Obligatorio.",
)
@click.option(
    "--end",
    type=str,
    default=None,
    help=(
        "Último día del rango, en formato YYYY-MM-DD (incluido). Obligatorio. "
        "Debe ser anterior al día actual (America/Caracas)."
    ),
)
@click.pass_context
def cli(context: click.Context, start: str | None, end: str | None) -> None:
    """Genera un reporte Excel de tráfico con los resúmenes diarios del rango.

    Calcula, por interfaz, el promedio de sus promedios diarios y el máximo de sus máximos
    diarios, en Gbps, y el porcentaje de uso. Crea un archivo .xlsx con una hoja por capa en
    el directorio export_path de config.yml. Solo lee la base de datos; termina al acabar.

    \b
    Códigos de salida:
      0  resultado general exitoso
      1  resultado general fallido (capa fallida, ninguna capa con datos, falla al escribir)
      2  error general del proceso (parámetros o configuración inválidos,
         base de datos no disponible, sin capas, error inesperado)
    """
    exit_code = execute(
        start=start,
        end=end,
        extra_arguments=context.args,
        environment=os.environ,
        clock=SystemClock(),
        log_path=Path(LOG_DIRECTORY) / LOG_FILE_NAME,
        output=sys.stdout,
        errors=sys.stderr,
    )
    sys.exit(exit_code)
