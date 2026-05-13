import logging
from os import path
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from scanbackup.shared.config.paths import PathConfig
from scanbackup.shared.config.metadata import (
    LOG_FILENAME,
    LOG_EXTENSION,
    LOG_FORMAT,
    DATE_FORMAT,
)

FILEPATH = Path(path.join(PathConfig.FOLDER_LOG, LOG_FILENAME + LOG_EXTENSION))
FORMATTER = logging.Formatter(LOG_FORMAT, DATE_FORMAT)


class LogHandler:
    """Handler to realize all operation about log system."""

    __file_handler: TimedRotatingFileHandler
    logger: logging.Logger

    def __init__(self) -> None:
        try:
            PathConfig.create_folder(PathConfig.FOLDER_LOG)
            self.__file_handler = TimedRotatingFileHandler(
                FILEPATH,
                when="W0",
                interval=1,
                backupCount=4,
                encoding="utf-8",
                utc=True,
            )
            self.__file_handler.setFormatter(FORMATTER)
            logging.basicConfig(
                level=logging.INFO,
                handlers=[self.__file_handler],
            )
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            print(f"Log Error - {e}")


logHandler = LogHandler()
Log = logHandler.logger

if __name__ == "__main__":
    print(f"Ubicación física: {FILEPATH}")  # TODO: Cambiar esto a una prueba unitaria
    logHandler.create_file()
    Log.info("Prueba de informe log")
