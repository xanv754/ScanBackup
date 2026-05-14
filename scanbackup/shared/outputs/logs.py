import logging
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from scanbackup.shared.config.paths import PathConfig
from scanbackup.shared.config.metadata import (
    LOG_FORMAT,
    DATE_FORMAT,
)

FORMATTER = logging.Formatter(LOG_FORMAT, DATE_FORMAT)


class LogHandler:
    """Handler to realize all operation about log system."""

    file_handler: TimedRotatingFileHandler
    filepath: Path = PathConfig.LOG_FILE
    logger: logging.Logger

    def __init__(self) -> None:
        try:
            PathConfig.create_folder(PathConfig.FOLDER_LOG)
            self.file_handler = TimedRotatingFileHandler(
                self.filepath,
                when="W0",
                interval=1,
                backupCount=4,
                encoding="utf-8",
                utc=True,
            )
            self.file_handler.setFormatter(FORMATTER)
            logging.basicConfig(
                level=logging.INFO,
                handlers=[self.file_handler],
            )
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            print(f"Log Error - {e}")
            exit(1)


handler = LogHandler()
Log = handler.logger

if __name__ == "__main__":
    print(
        f"Ubicación física: {handler.filepath}"
    )  # TODO: Cambiar esto a una prueba unitaria
    Log.info("Prueba de informe log")
