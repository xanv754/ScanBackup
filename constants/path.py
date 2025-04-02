from os import getcwd
from enum import Enum


class SystemConstant(Enum):
    """All constants neccessary to the system."""

    TITLE_PROJECT = "SystemCGPRD"
    FILEPATH_LOGS = f"{getcwd()}/system.log"
