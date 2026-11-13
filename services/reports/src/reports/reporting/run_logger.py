import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from reports.constants.constants import (
    LOG_BACKUP_COUNT,
    LOG_FORMAT,
    LOG_MAX_BYTES,
    LOGGER_NAME,
    TEXT_ENCODING,
)
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


def create_file_logger(log_path: Path) -> logging.Logger:
    """Return the service logger writing to a rotating file at `log_path` [RF-045].

    The file is opened in append mode, so the messages of previous runs are kept. The file and
    its directory are created if needed. Calling it again replaces the handler.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for existing_handler in list(logger.handlers):
        existing_handler.close()
        logger.removeHandler(existing_handler)
    handler = RotatingFileHandler(
        log_path,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding=TEXT_ENCODING,
    )
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger


class RunLogger(EventSink):
    """Writes the events of the run to the log file [RF-045].

    Nothing is logged per interface: only the layers, the warnings, the file and the results.
    Events carry no secrets, so nothing sensitive reaches the file.
    """

    def __init__(self, logger: logging.Logger) -> None:
        """Receive the logger to write to."""
        self._logger = logger

    def publish(self, event: Event) -> None:
        match event:
            case RunStarted():
                date_range = event.date_range
                self._logger.info(
                    "Inicio de la ejecución: rango %s a %s (%d días)",
                    date_range.start_key,
                    date_range.end_key,
                    date_range.day_count,
                )
            case ProcessFailed():
                for cause in event.causes:
                    self._logger.error("Error general: %s", cause)
            case LayerEmpty():
                self._logger.warning("Capa %s: sin datos en el rango", event.layer)
            case LayerFailed():
                self._logger.error("Capa %s fallida: %s", event.layer, event.cause)
            case LayerIncomplete():
                self._logger.warning(
                    "Capa %s: %d interfaces con menos resúmenes que los días del rango",
                    event.layer,
                    event.interface_count,
                )
            case LayerFinished():
                result = event.result
                level = logging.ERROR if result.failed else logging.INFO
                self._logger.log(
                    level,
                    "Capa %s %s: %d interfaces incluidas",
                    result.layer,
                    "fallida" if result.failed else "exitosa",
                    result.included_count,
                )
            case MissingDay():
                self._logger.warning("Día del rango sin resúmenes: %s", event.day)
            case FileGenerated():
                summary = event.summary
                self._logger.info(
                    "Archivo generado: %s en %s (%d hojas, %d interfaces exportadas)",
                    summary.path.name,
                    summary.path.parent,
                    summary.sheet_count,
                    summary.interface_count,
                )
            case ExportFailed():
                self._logger.error(
                    "Falla en la generación del archivo: %s", event.cause
                )
            case RunFinished():
                result = event.result
                if result.failed:
                    self._logger.error(
                        "Resultado general: fallido (capas fallidas: %s)",
                        ", ".join(result.failed_layers) or "ninguna",
                    )
                else:
                    self._logger.info("Resultado general: exitoso")

    def close(self) -> None:
        """Release the handlers of the logger."""
        for handler in list(self._logger.handlers):
            handler.close()
            self._logger.removeHandler(handler)
