import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class ServiceLogger:
    """Writes service events to a log file that rotates weekly (Sunday to Saturday).

    Each line follows the format `<date> <level> <message> - <details>`.
    The `details` part is optional; when omitted, only the message is written.
    """

    LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    DETAILS_SEPARATOR = " - "
    ROTATION_DAY = "W5"
    ROTATION_SUFFIX = "%Y-%m-%d"

    def __init__(
        self,
        log_file_path: Path,
        logger_name: str = "interface_sync",
        retained_weeks: int = 12,
    ) -> None:
        """Create the log directory and attach a weekly rotating file handler.

        The handler rolls over at midnight between Saturday and Sunday, using the
        local timezone of the process. Rotated files are kept up to `retained_weeks`.
        """
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        if not self._logger.handlers:
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            handler = TimedRotatingFileHandler(
                filename=log_file_path,
                when=self.ROTATION_DAY,
                backupCount=retained_weeks,
                encoding="utf-8",
            )
            handler.suffix = self.ROTATION_SUFFIX
            handler.setFormatter(logging.Formatter(self.LOG_FORMAT, self.DATE_FORMAT))
            self._logger.addHandler(handler)

    def info(self, message: str, details: str = "") -> None:
        """Register an informational event."""
        self._logger.info(self._compose(message, details))

    def warning(self, message: str, details: str = "") -> None:
        """Register an event that does not stop the process but needs attention."""
        self._logger.warning(self._compose(message, details))

    def error(self, message: str, details: str = "") -> None:
        """Register a failure event."""
        self._logger.error(self._compose(message, details))

    def _compose(self, message: str, details: str) -> str:
        """Join the general message with its details when details are provided."""
        if not details:
            return message
        return f"{message}{self.DETAILS_SEPARATOR}{details}"
