import os
import sys
from collections.abc import Mapping
from datetime import date, datetime
from pathlib import Path
from typing import TextIO

import click

from traffic_collector.clock import CARACAS_TIMEZONE, TargetDate
from traffic_collector.collection import (
    DailySummaryCalculator,
    DailySummaryPhase,
    InterfaceProcessor,
    LayerProcessor,
    RunOrchestrator,
)
from traffic_collector.constants.constants import (
    DATABASE_UNAVAILABLE_CAUSE,
    LOG_DIRECTORY,
    LOG_FILE_ERROR_CAUSE,
    LOG_FILE_NAME,
    UNEXPECTED_ERROR_CAUSE,
)
from traffic_collector.constants.enums import ExitCode
from traffic_collector.exceptions import DatabaseError, ProcessError
from traffic_collector.parsing import DayFilter, LogParser, SampleValidator
from traffic_collector.persistence import (
    InterfaceRepository,
    MongoConnection,
    SummaryRepository,
    TrafficRepository,
)
from traffic_collector.reporting import (
    CompositeEventSink,
    EventSink,
    ProcessFailed,
    RunLogger,
    TerminalReporter,
    create_file_logger,
)
from traffic_collector.scan import HttpScanClient
from traffic_collector.settings import Settings, SettingsLoader


def execute(
    force: bool,
    environment: Mapping[str, str],
    today: date,
    log_path: Path,
    output: TextIO,
    errors: TextIO,
) -> ExitCode:
    """Assemble every dependency, run the collection and return the process exit code.

    The previous day is calculated here once and shared by every component. Any error that
    prevents the collection is reported and returns `ExitCode.PROCESS_ERROR`.
    """
    terminal = TerminalReporter(output, errors)
    try:
        run_logger = RunLogger(create_file_logger(log_path))
    except OSError as error:
        terminal.publish(ProcessFailed((f"{LOG_FILE_ERROR_CAUSE} ({error})",)))
        return ExitCode.PROCESS_ERROR

    event_sink = CompositeEventSink((run_logger, terminal))
    connection: MongoConnection | None = None
    scan_client: HttpScanClient | None = None
    try:
        settings = SettingsLoader(environment).load()
        target_date = TargetDate.previous_day(today)
        connection = MongoConnection(settings.mongo)
        scan_client = HttpScanClient(
            settings.scan, settings.collection.request_timeout_seconds
        )
        orchestrator = _build_orchestrator(
            force, target_date, settings, connection, scan_client, event_sink
        )
        return orchestrator.run().exit_code
    except ProcessError as error:
        event_sink.publish(ProcessFailed(tuple(error.causes)))
    except DatabaseError as error:
        event_sink.publish(ProcessFailed((DATABASE_UNAVAILABLE_CAUSE,), error))
    except Exception as error:
        event_sink.publish(
            ProcessFailed(
                (f"{UNEXPECTED_ERROR_CAUSE}: {type(error).__name__}: {error}",), error
            )
        )
    finally:
        if scan_client is not None:
            scan_client.close()
        if connection is not None:
            connection.close()
        run_logger.close()
    return ExitCode.PROCESS_ERROR


def _build_orchestrator(
    force: bool,
    target_date: TargetDate,
    settings: Settings,
    connection: MongoConnection,
    scan_client: HttpScanClient,
    event_sink: EventSink,
) -> RunOrchestrator:
    """Create the repositories and processors and wire them into the orchestrator."""
    database = connection.database
    interface_repository = InterfaceRepository(database)
    traffic_repository = TrafficRepository(database)
    traffic_repository.ensure_indexes()
    summary_repository = SummaryRepository(database)
    summary_repository.ensure_indexes()
    interface_processor = InterfaceProcessor(
        target_date=target_date,
        force=force,
        parser=LogParser(),
        day_filter=DayFilter(target_date),
        validator=SampleValidator(),
        traffic_store=traffic_repository,
        summary_store=summary_repository,
    )
    layer_processor = LayerProcessor(
        target_date=target_date,
        force=force,
        config=settings.collection,
        interface_reader=interface_repository,
        traffic_store=traffic_repository,
        scan_client=scan_client,
        interface_processor=interface_processor,
        event_sink=event_sink,
    )
    return RunOrchestrator(
        target_date=target_date,
        interface_reader=interface_repository,
        layer_collector=layer_processor,
        summary_phase=DailySummaryPhase(
            traffic_reader=traffic_repository,
            summary_writer=summary_repository,
            calculator=DailySummaryCalculator(),
            event_sink=event_sink,
        ),
        event_sink=event_sink,
    )


@click.command(name="traffic_collector")
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Vuelve a consultar las interfaces que ya tienen valores del día anterior.",
)
def cli(force: bool) -> None:
    """Respalda el tráfico del día anterior de las interfaces activas desde SCAN.

    Procesa todas las capas y termina; no queda ningún proceso. Una (1) ejecución
    programada por día vía crontab; puede reejecutarse el mismo día. Las credenciales
    de SCAN se toman de SCAN_USERNAME y SCAN_PASSWORD.

    \b
    Códigos de salida:
      0  todas las capas se completaron con éxito
      1  resultado general fallido (capas o interfaces fallidas, sin interfaces activas)
      2  error general del proceso (configuración inválida, credenciales ausentes,
         base de datos no disponible, sin capas, error inesperado)
    """
    exit_code = execute(
        force=force,
        environment=os.environ,
        today=datetime.now(CARACAS_TIMEZONE).date(),
        log_path=Path(LOG_DIRECTORY) / LOG_FILE_NAME,
        output=sys.stdout,
        errors=sys.stderr,
    )
    sys.exit(exit_code)
