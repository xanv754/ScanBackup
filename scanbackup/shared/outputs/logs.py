import logging
from os import makedirs
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from scanbackup.shared.config.config import Configuration


class LogHandler:
    """Handler to realize all operation about log system."""

    file_handler: TimedRotatingFileHandler
    logger: logging.Logger
    filepath: str

    def __init__(self) -> None:
        try:
            config = Configuration()
            metadata = config.get_cfg_metadata()
            log_cfg = metadata.logs

            filepath = Path(
                Path(__file__).resolve().parent.parent.parent.parent
                / metadata.dir_data
                / log_cfg.dir_name
                / f"{log_cfg.filename}.{log_cfg.extension}"
            )

            if not filepath.exists():
                makedirs(filepath.parent, exist_ok=True)

            formatter = logging.Formatter(log_cfg.msg_format, log_cfg.date_format)

            self.file_handler = TimedRotatingFileHandler(
                filepath,
                when="W0",
                interval=1,
                backupCount=4,
                encoding="utf-8",
                utc=True,
            )
            self.file_handler.setFormatter(formatter)
            logging.basicConfig(
                level=logging.INFO,
                handlers=[self.file_handler],
            )
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            print(f"Log Error - {e}")
            exit(1)
        else:
            self.filepath = filepath.resolve()


LOG_HANDLER = LogHandler()
Log = LOG_HANDLER.logger

if __name__ == "__main__":
    print(
        f"Ubicación física: {LOG_HANDLER.filepath}"
    )  # TODO: Cambiar esto a una prueba unitaria
    Log.info("Prueba de informe log")
