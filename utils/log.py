import rich
from datetime import datetime
from constants import SystemConstant


class LogHandler:
    """Handler to realize all operation about log system."""

    @staticmethod
    def save(message: str, script: str, err: bool = False, warning: bool = False, info: bool = False) -> None:
        """Save a message on the log file of system. Also print message in terminal.

        Parameters
        ----------
        message : str
            Message to save on the log file.
        script : str
            Path of file that called the function.
        err : bool
            If the message is an error. Default false.
        warning : bool
            If the message is an warning. Default false.
        info : bool
            If the message is an info. Default false.
        """
        script = script.split(f"/{SystemConstant.TITLE_PROJECT.value}/")[1]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if err:
            rich.print(f"[red3] [{date}] ({script}) Error: [default]{message}")
            message = f"[{date}] ({script}) Error: {message}"
        elif warning:
            rich.print(f"[orange3] [{date}] ({script}) Warning: [default]{message}")
            message = f"[{date}] ({script}) Warning: {message}"
        elif info:
            rich.print(f"[green3] [{date}] ({script}) Info: [default]{message}")
            message = f"[{date}] ({script}) Info: {message}"
        else:
            message = f"[{date}] ({script}): {message}"
            print(message)
        with open(SystemConstant.FILEPATH_LOGS.value, "a") as file:
            file.write(f"{message}\n")


if __name__ == "__main__":
    LogHandler.save("This is a test", __file__, err=True)
    LogHandler.save("This is a test", __file__, warning=True)
    LogHandler.save("This is a test", __file__, info=True)
