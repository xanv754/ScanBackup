import logging
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from rich.logging import RichHandler

# TITLE_ART = art.text2art(f"{AboutConstant.TITLE_CLI.value}")
LOGS = "/var/log/cgprd"
LOG_FORMAT = "%(asctime)s %(levelname)s (%(filename)s) %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
FORMATTER = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

class LogHandler:
    """Handler to realize all operation about log system."""

    __console_handler: RichHandler
    __file_handler: TimedRotatingFileHandler
    logger: logging.Logger

    def __init__(self) -> None:
        try:
            folder_exist = self.create_file()
            if not folder_exist: return
            self.__console_handler = RichHandler(
                rich_tracebacks=True,
                markup=False,
                show_path=False,
                show_time=False,
                show_level=False,
            )
            self.__console_handler.setFormatter(FORMATTER)
            self.__file_handler = TimedRotatingFileHandler(
                f"{LOGS}/system-cgprd.log",
                when="W0",
                interval=1,
                backupCount=4,
                encoding="utf-8",
                utc=True
            )
            self.__file_handler.setFormatter(FORMATTER)
            logging.basicConfig(level=logging.INFO, handlers=[self.__console_handler, self.__file_handler])
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            print(f"Log Error - {e}")

    def create_file(self) -> bool:
        """Create file to save logs."""
        try:
            path = Path(LOGS)
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(e)
            return False


logHandler = LogHandler()
log = logHandler.logger

if __name__ == "__main__":
    logHandler.create_file()
    log.info("Test")

