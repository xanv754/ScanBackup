import rich
import art
from typing import Set, List
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
    __register: Set = set()
    __console: Console
    __started: bool = False

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(LogHandler, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        try:
            if not hasattr(self, "__initialized"):
                self.__console = Console()
                self.__initialized = True
        except Exception as e:
            rich.print(f"Log Error - {e}")


    def __cprint(self, message: str, path: str | None = None, err: bool = False, warn: bool = False, info: bool = False) -> None:
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
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        date_complete = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if err and path:
            path = path.split(f"/{AboutConstant.TITLE_PROJECT.value}/")[1]
            message_print = Text.assemble(
                (date_complete, "orange3"),
                (f" ({path})", "deep_sky_blue1"),
                (f" ERROR", "red3"),
                (f" {message}")
            )
            message_str = f"{date} ({path}) ERROR {message}"
        elif err:
            message_print = Text.assemble(
                (date_complete, "orange3"),
                (f" ERROR", "red3"),
                (f" {message}")
            )
            message_str = f"{date} ERROR {message}"
        elif warn and path:
            path = path.split(f"/{AboutConstant.TITLE_PROJECT.value}/")[1]
            message_print = Text.assemble(
                (date_complete, "orange3"),
                (f" ({path})", "deep_sky_blue1"),
                (f" WARNING", "gold1"),
                (f" {message}")
            )
            message_str = f"{date} ({path}) WARNING {message}"
        elif warn:
            message_print = Text.assemble(
                (date_complete, "orange3"),
                (f" WARNING", "gold1"),
                (f" {message}")
            )
            message_str = f"{date} WARNING {message}"
        elif info and path:
            path = path.split(f"/{AboutConstant.TITLE_PROJECT.value}/")[1]
            message_print = Text.assemble(
                (date_complete, "orange3"),
                (f" ({path})", "deep_sky_blue1"),
                (f" INFO", "chartreuse2"),
                (f" {message}")
            )
            message_str = f"{date} ({path}) INFO {message}"
        elif info:
            message_print = Text.assemble(
                (date_complete, "orange3"),
                (f" INFO", "chartreuse2"),
                (f" {message}")
            )
            message_str = f"{date} INFO {message}"
        elif not err and not warn and not info and path:
            path = path.split(f"/{AboutConstant.TITLE_PROJECT.value}/")[1]
            message_print = Text.assemble(
                (date_complete, "orange3"),
                (f" ({path})", "deep_sky_blue1"),
                (f" {message}")
            )
            message_str = f"{date} ({path}) {message}"
        else:
            message_print = Text.assemble(
                (date_complete, "orange3"),
                (f" ({path})", "deep_sky_blue1"),
                (f" {message}")
            )
            message_str = f"{date} {message}"
        if not message_str in self.__register:
            self.__register.add(message_str)
            if not self.__started:
                self.__console.print(Text(f"{TITLE_ART}", "dark_slate_gray2"))
                self.__started = True
            self.__console.print(message_print)

    def __save(self, message: str, path: str | None = None, err: bool = False, warn: bool = False, info: bool = False) -> None:
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

    def export(self, message: str, path: str | None = None, err: bool = False, warn: bool = False, info: bool = False, cprint: bool = True) -> None:
        message = message.strip()
        if cprint:
            self.__cprint(message, path=path, err=err, warn=warn, info=info)
        self.__save(message, path=path, err=err, warn=warn, info=info)

    def print(self, message: any, path: str | None = None) -> None:
        message = str(message)
        messages: List[str] = []
        if path:
            path = path.split(f"/{AboutConstant.TITLE_PROJECT.value}/")[1]
            messages.append(f"Path print: {path}\n")
        messages.append(message)
        group = Group(*messages)
        panel = Panel(group, title="Debug", style="dark_slate_gray2", title_align="left")
        self.__console.print(panel)

if __name__ == "__main__":
    log = LogHandler()
    log.export("This is a test", path=__file__, err=True)
    log.export("This is a test", path=__file__, warn=True)
    log.print("This is a test", path=__file__)
    log.export("This is a test", path=__file__, info=True)
