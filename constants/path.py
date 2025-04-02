from os import getcwd
from enum import Enum


class PathConstant(Enum):
    """All paths neccessary to the system."""

    FILEPATH_LOGS = f"{getcwd()}/system.log"
