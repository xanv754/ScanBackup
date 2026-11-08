import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from traffic_collector.constants.constants import (
    LOG_BACKUP_COUNT,
    LOG_FORMAT,
    LOG_MAX_BYTES,
    LOGGER_NAME,
    TEXT_ENCODING,
)
from traffic_collector.reporting.events import (
    Event,
    InterfaceFailed,
    InterfaceInvalidLines,
    InterfaceSampleCountWarning,
    LayerCut,
    LayerEmpty,
    LayerFinished,
    LayerReadFailed,
    LayerStarted,
    ProcessFailed,
    RunFinished,
    SummaryPending,
)


def create_file_logger(log_path: Path) -> logging.Logger:
    """Return the service logger writing to a rotating file at `log_path` [RF-029].

    The file is created with its directory if needed. Calling it again replaces the handler.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for existing_handler in list(logger.handlers):
        existing_handler.close()
        logger.removeHandler(existing_handler)
    handler = RotatingFileHandler(
        log_path, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding=TEXT_ENCODING
    )
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger


class RunLogger:
    """Writes the events of the run to the log file [RF-029].

    Successful interfaces are not logged one by one: only warnings, errors and the summary of
    each layer. Events carry no secrets, so nothing sensitive reaches the file.
    """

    def __init__(self, logger: logging.Logger) -> None:
        """Receive the logger to write to."""
        self._logger = logger

    def publish(self, event: Event) -> None:
        """Write the event with the level that matches it."""
        match event:
            case LayerStarted():
                self._logger.info(
                    "Capa %s: %d interfaces activas, %d omitidas",
                    event.layer,
                    event.active_count,
                    event.skipped_count,
                )
            case LayerEmpty():
                self._logger.warning("Capa %s: sin interfaces activas", event.layer)
            case LayerReadFailed():
                self._logger.error(
                    "Capa %s: no se pudieron leer sus interfaces de la base de datos", event.layer
                )
            case InterfaceFailed():
                self._logger.error(
                    "Capa %s: interfaz %s (%s) fallida: %s",
                    event.layer,
                    event.interface.interface_id,
                    event.interface.scan_url,
                    event.cause.value,
                )
            case InterfaceSampleCountWarning():
                self._logger.warning(
                    "Capa %s: interfaz %s (%s) almacenada con %d muestras (%s)",
                    event.layer,
                    event.interface.interface_id,
                    event.interface.scan_url,
                    event.sample_count,
                    event.verdict.value,
                )
            case InterfaceInvalidLines():
                self._logger.warning(
                    "Capa %s: interfaz %s (%s) con %d líneas inválidas descartadas",
                    event.layer,
                    event.interface.interface_id,
                    event.interface.scan_url,
                    event.line_count,
                )
            case LayerCut():
                self._logger.error(
                    "Capa %s: procesamiento cortado por %s; %d interfaces sin procesar",
                    event.layer,
                    event.reason.value,
                    event.not_processed_count,
                )
            case LayerFinished():
                result = event.result
                level = logging.ERROR if result.failed else logging.INFO
                self._logger.log(
                    level,
                    "Capa %s %s: %d almacenadas, %d omitidas, %d fallidas, %d sin procesar",
                    result.layer,
                    "fallida" if result.failed else "exitosa",
                    result.stored_count,
                    result.skipped_count,
                    result.failed_count,
                    result.not_processed_count,
                )
            case SummaryPending():
                self._logger.warning("Resumen diario pendiente de implementar (RF-026)")
            case ProcessFailed():
                for cause in event.causes:
                    self._logger.error("Error general: %s", cause, exc_info=event.error)
            case RunFinished():
                self._logger.log(
                    logging.ERROR if event.result.failed else logging.INFO,
                    "Resultado general: %s",
                    "fallido" if event.result.failed else "exitoso",
                )

    def close(self) -> None:
        """Flush and close the handlers of the logger."""
        for handler in list(self._logger.handlers):
            handler.close()
            self._logger.removeHandler(handler)
