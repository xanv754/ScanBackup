from rich.status import Status
from rich.console import Console as RichConsole


class Terminal:
    _instance: "Terminal | None" = None
    _console: RichConsole = RichConsole(log_path=False)

    def __new__(cls) -> "Terminal":
        if cls._instance is None:
            cls._instance = super(Terminal, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def info(message: str, preffix: str | None = None) -> None:
        message = f"[default]{message}"
        if preffix:
            message = f"[green3]{preffix} INFO: " + message
        Terminal._console.log(message)

    @staticmethod
    def warning(message: str, preffix: str | None = None) -> None:
        message = f"[default]{message}"
        if preffix:
            message = f"[orange3]{preffix} WARNING: " + message
        Terminal._console.log(message)

    @staticmethod
    def error(message: str, preffix: str | None = None) -> None:
        message = f"[default]{message}"
        if preffix:
            message = f"[red3]{preffix} ERROR: " + message
        Terminal._console.log(message)

    @staticmethod
    def loading(status: Status, message: str) -> None:
        status.update(message)

    @classmethod
    def status(cls, initial_message: str) -> Status:
        return cls._console.status(initial_message)
