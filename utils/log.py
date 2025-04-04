import rich
import art
from typing import List
from datetime import datetime
from rich.text import Text
from rich.console import Console, Group
from rich.panel import Panel
from constants.path import PathConstant
from constants.about import AboutConstant

TITLE_ART = art.text2art(f"{AboutConstant.TITLE_CLI.value}")

class LogHandler:
    """Handler to realize all operation about log system."""

    __instance:  "LogHandler | None" = None
    __stdout: List[Text] = [Text(f"{TITLE_ART}", "dark_slate_gray2")]
    __console: Console

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(LogHandler, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        try:
            if not hasattr(self, "__initialized"):
                self.__initialized = True
                self.__console = Console()
        except Exception as e:
            rich.print(f"Log Error - {e}")

    @classmethod
    def log(cls, message: str, path: str | None = None, err: bool = False, warn: bool = False, info: bool = False, cprint: bool = True) -> None:
        instance = cls.__new__(cls)
        instance.__init__()
        if cprint:
            instance.cprint(message, path=path, err=err, warn=warn, info=info)
        instance.save(message, path=path, err=err, warn=warn, info=info)

    def cprint(self, message: str, path: str | None = None, err: bool = False, warn: bool = False, info: bool = False) -> None:
        """Print message in terminal.

        Parameters
        ----------
        message : str
            Message to save on the log file.
        path : str
            Path of file that called the function.
        err : bool
            If the message is an error. Default false.
        warning : bool
            If the message is an warning. Default false.
        info : bool
            If the message is an info. Default false.
        """
        if path:
            path = path.split(f"/{AboutConstant.TITLE_PROJECT.value}/")[1]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if err:
            if path:
                message_print = Text.assemble(
                    (date, "orange3"),
                    (f" ({path})", "deep_sky_blue1"),
                    (f" ERROR", "red3"),
                    (f" {message}")
                )
            else:
                message_print = Text.assemble(
                    (date, "orange3"),
                    (f" ERROR", "red3"),
                    (f" {message}")
                )
        elif warn:
            if path:
                message_print = Text.assemble(
                    (date, "orange3"),
                    (f" ({path})", "deep_sky_blue1"),
                    (f" WARNING", "gold1"),
                    (f" {message}")
                )
            else:
                message_print = Text.assemble(
                    (date, "orange3"),
                    (f" WARNING", "gold1"),
                    (f" {message}")
                )
        elif info:
            if path:
                message_print = Text.assemble(
                    (date, "orange3"),
                    (f" ({path})", "deep_sky_blue1"),
                    (f" INFO", "chartreuse2"),
                    (f" {message}")
                )
            else:
                message_print = Text.assemble(
                    (date, "orange3"),
                    (f" INFO", "chartreuse2"),
                    (f" {message}")
                )
        else:
            if path:
                message_print = Text.assemble(
                    (date, "orange3"),
                    (f" ({path})", "deep_sky_blue1"),
                    (f" {message}")
                )
            else:
                message_print = Text.assemble(
                    (date, "orange3"),
                    (f" {message}")
                )
        self.__stdout.append(message_print)
        group = Group(*self.__stdout)
        panel = Panel(group, title="Sistema CGPRD", style="dark_slate_gray2")
        self.__console.clear()
        self.__console.print(panel)

    def save(self, message: str, path: str | None = None, err: bool = False, warn: bool = False, info: bool = False) -> None:
        """Save a message on the log file of system. Also print message in terminal.

        Parameters
        ----------
        message : str
            Message to save on the log file.
        path : str
            Path of file that called the function.
        err : bool
            If the message is an error. Default false.
        warning : bool
            If the message is an warning. Default false.
        info : bool
            If the message is an info. Default false.
        """
        if path:
            path = path.split(f"/{AboutConstant.TITLE_PROJECT.value}/")[1]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if err:
            if path:
                message = f"{date} ({path}) ERROR - {message}"
            else:
                message = f"{date} ERROR - {message}"
        elif warn:
            if path:
                message = f"{date} ({path}) WARNING - {message}"
            else:
                message = f"{date} WARNING - {message}"
        elif info:
            if path:
                message = f"{date} ({path}) INFO - {message}"
            else:
                message = f"{date} INFO - {message}"
        else:
            if path:
                message = f"{date} ({path}) - {message}"
            else:
                message = f"{date} - {message}"
        with open(PathConstant.FILEPATH_LOGS, "a") as file:
            file.write(f"{message}\n")


if __name__ == "__main__":
    LogHandler.log("This is a test", path=__file__, err=True)
    LogHandler.log("This is a test", path=__file__, warn=True)
    LogHandler.log("This is a test", path=__file__, info=True)
