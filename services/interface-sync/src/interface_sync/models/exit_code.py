from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes of the service process."""

    SUCCESS = 0
    FAILED = 1
    PROCESS_ERROR = 2
