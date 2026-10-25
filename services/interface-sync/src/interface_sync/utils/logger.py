import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from interface_sync.constants.constants import (
    DATE_FORMAT,
    LOG_DETAILS_SEPARATOR,
    LOG_FORMAT,
    LOG_ROTATION_DAY,
    LOG_ROTATION_SUFFIX,
    LOGGER_NAME,
    TEXT_ENCODING,
)


class ServiceLogger:
    """Writes service events to a log file that rotates weekly (Sunday to Saturday).

    Each line follows the format `<date> <level> <message> - <details>`.
    The `details` part is optional; when omitted, only the message is written.
    """

    def __init__(
        self,
        log_file_path: Path,
        logger_name: str = LOGGER_NAME,
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
                when=LOG_ROTATION_DAY,
                backupCount=retained_weeks,
                encoding=TEXT_ENCODING,
            )
            handler.suffix = LOG_ROTATION_SUFFIX
            handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
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
        return f"{message}{LOG_DETAILS_SEPARATOR}{details}"
