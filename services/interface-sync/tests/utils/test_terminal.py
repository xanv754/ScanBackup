import io
import re

import pytest
from rich.console import Console

from interface_sync.utils.terminal import Terminal

DATE_PATTERN = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def build_console(is_terminal: bool) -> tuple[Console, io.StringIO]:
    buffer = io.StringIO()
    console = Console(
        file=buffer,
        force_terminal=is_terminal,
        color_system="standard" if is_terminal else None,
        width=200,
    )
    return console, buffer


@pytest.fixture
def output_buffer() -> io.StringIO:
    return io.StringIO()


@pytest.fixture
def error_buffer() -> io.StringIO:
    return io.StringIO()


@pytest.fixture
def plain_terminal(output_buffer: io.StringIO, error_buffer: io.StringIO) -> Terminal:
    output_console = Console(file=output_buffer, color_system=None, width=200)
    error_console = Console(file=error_buffer, color_system=None, width=200)
    return Terminal(output_console, error_console)


@pytest.mark.parametrize(
    ("method_name", "level"),
    [("info", "INFO"), ("warning", "WARNING"), ("error", "ERROR")],
)
def test_message_has_date_level_and_text(
    plain_terminal: Terminal,
    output_buffer: io.StringIO,
    error_buffer: io.StringIO,
    method_name: str,
    level: str,
) -> None:
    """RF-015: every terminal line shows date, level and message."""
    getattr(plain_terminal, method_name)("Page processed")

    written = (error_buffer if level == "ERROR" else output_buffer).getvalue()
    assert re.fullmatch(rf"{DATE_PATTERN} {level} Page processed\n", written)


def test_error_goes_to_stderr_only(
    plain_terminal: Terminal,
    output_buffer: io.StringIO,
    error_buffer: io.StringIO,
) -> None:
    """RF-015: general process errors are written to stderr."""
    plain_terminal.error("Invalid configuration")

    assert output_buffer.getvalue() == ""
    assert "Invalid configuration" in error_buffer.getvalue()


def test_info_and_warning_go_to_stdout_only(
    plain_terminal: Terminal,
    output_buffer: io.StringIO,
    error_buffer: io.StringIO,
) -> None:
    """RF-015: non-error messages are written to stdout."""
    plain_terminal.info("Started")
    plain_terminal.warning("Incomplete interface")

    assert error_buffer.getvalue() == ""
    assert "INFO" in output_buffer.getvalue()
    assert "WARNING" in output_buffer.getvalue()


@pytest.mark.parametrize(
    ("method_name", "level", "ansi_color_code"),
    [("info", "INFO", "32"), ("warning", "WARNING", "33"), ("error", "ERROR", "31")],
)
def test_only_level_is_colored(method_name: str, level: str, ansi_color_code: str) -> None:
    """RF-015: INFO is green, WARNING yellow, ERROR red; the message keeps default color."""
    output_console, output_buffer = build_console(is_terminal=True)
    error_console, error_buffer = build_console(is_terminal=True)
    terminal = Terminal(output_console, error_console)

    getattr(terminal, method_name)("Some message")

    written = (error_buffer if level == "ERROR" else output_buffer).getvalue()
    assert f"\x1b[{ansi_color_code}m{level}\x1b[0m" in written
    assert "Some message" in ANSI_PATTERN.sub("", written)
    assert re.search(r"\x1b\[[0-9;]*mSome message", written) is None


def test_message_markup_is_not_interpreted(
    plain_terminal: Terminal, output_buffer: io.StringIO
) -> None:
    """RF-015: messages are printed literally, including Rich-like markup."""
    plain_terminal.info("Page [bold]http://scan/host[/bold] failed")

    assert "Page [bold]http://scan/host[/bold] failed" in output_buffer.getvalue()


def test_long_message_is_not_truncated(
    output_buffer: io.StringIO, error_buffer: io.StringIO
) -> None:
    """RF-015: long messages are kept whole in a single line."""
    narrow_console = Console(file=output_buffer, color_system=None, width=20)
    terminal = Terminal(narrow_console, Console(file=error_buffer, width=20))
    long_message = "x" * 100

    terminal.info(long_message)

    assert long_message in output_buffer.getvalue().replace("\n", "")


def test_loading_runs_wrapped_operation(plain_terminal: Terminal) -> None:
    """RF-015: the spinner context lets the wrapped operation run."""
    executed: list[str] = []

    with plain_terminal.loading("Loading pages"):
        executed.append("done")

    assert executed == ["done"]


def test_loading_propagates_exception(plain_terminal: Terminal) -> None:
    """RF-015: the spinner does not swallow errors of the wrapped operation."""
    with pytest.raises(RuntimeError, match="boom"), plain_terminal.loading("Loading pages"):
        raise RuntimeError("boom")


def test_loading_uses_stdout_console() -> None:
    """RF-015: the spinner is rendered on stdout, never on stderr."""
    output_console, output_buffer = build_console(is_terminal=True)
    error_console, error_buffer = build_console(is_terminal=True)
    terminal = Terminal(output_console, error_console)

    with terminal.loading("Loading pages"):
        pass

    assert error_buffer.getvalue() == ""
    assert "Loading pages" in output_buffer.getvalue()
