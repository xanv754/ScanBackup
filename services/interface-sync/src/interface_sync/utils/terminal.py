from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime

from rich.console import Console
from rich.text import Text


class Terminal:
    """Prints service events to the terminal using Rich.

    Each line follows the format `<date> <level> <message>`. The level is colored
    (`INFO` green, `WARNING` yellow, `ERROR` red) and the message keeps the default
    color of the terminal. `ERROR` lines are written to `stderr`; the rest to `stdout`.
    """

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    INFO_STYLE = "green"
    WARNING_STYLE = "yellow"
    ERROR_STYLE = "red"
    SPINNER_NAME = "dots"

    def __init__(
        self,
        output_console: Console | None = None,
        error_console: Console | None = None,
    ) -> None:
        """Use the given consoles, or create the default ones for `stdout` and `stderr`."""
        self._output_console = output_console or Console()
        self._error_console = error_console or Console(stderr=True)

    def info(self, message: str) -> None:
        """Print an informational message."""
        self._print(self._output_console, "INFO", self.INFO_STYLE, message)

    def warning(self, message: str) -> None:
        """Print a message about an event that needs attention."""
        self._print(self._output_console, "WARNING", self.WARNING_STYLE, message)

    def error(self, message: str) -> None:
        """Print a failure message to `stderr`."""
        self._print(self._error_console, "ERROR", self.ERROR_STYLE, message)

    @contextmanager
    def loading(self, message: str) -> Iterator[None]:
        """Show a spinner with the given message while the wrapped operation runs.

        The spinner is removed when the block ends, even if it raises. On non-interactive
        terminals Rich does not animate it.
        """
        with self._output_console.status(message, spinner=self.SPINNER_NAME):
            yield

    def _print(self, console: Console, level: str, level_style: str, message: str) -> None:
        """Compose and print a line without interpreting markup or highlighting the message."""
        line = Text()
        line.append(datetime.now().strftime(self.DATE_FORMAT))
        line.append(" ")
        line.append(level, style=level_style)
        line.append(" ")
        line.append(message)
        console.print(line, highlight=False, soft_wrap=True)
