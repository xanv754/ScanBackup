from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime

from rich.console import Console
from rich.text import Text

from interface_sync.constants.constants import (
    DATE_FORMAT,
    TERMINAL_LEVEL_STYLES,
    TERMINAL_SPINNER_NAME,
)
from interface_sync.constants.enums import TerminalLevel


class Terminal:
    """Prints service events to the terminal using Rich.

    Each line follows the format `<date> <level> <message>`. The level is colored
    (`INFO` green, `WARNING` yellow, `ERROR` red) and the message keeps the default
    color of the terminal. `ERROR` lines are written to `stderr`; the rest to `stdout`.
    """

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
        self._print(self._output_console, TerminalLevel.INFO, message)

    def warning(self, message: str) -> None:
        """Print a message about an event that needs attention."""
        self._print(self._output_console, TerminalLevel.WARNING, message)

    def error(self, message: str) -> None:
        """Print a failure message to `stderr`."""
        self._print(self._error_console, TerminalLevel.ERROR, message)

    @contextmanager
    def loading(self, message: str) -> Iterator[None]:
        """Show a spinner with the given message while the wrapped operation runs.

        The spinner is removed when the block ends, even if it raises. On non-interactive
        terminals Rich does not animate it.
        """
        with self._output_console.status(message, spinner=TERMINAL_SPINNER_NAME):
            yield

    def _print(self, console: Console, level: TerminalLevel, message: str) -> None:
        """Compose and print a line without interpreting markup or highlighting the message."""
        line = Text()
        line.append(datetime.now().strftime(DATE_FORMAT))
        line.append(" ")
        line.append(level, style=TERMINAL_LEVEL_STYLES[level])
        line.append(" ")
        line.append(message)
        console.print(line, highlight=False, soft_wrap=True)
