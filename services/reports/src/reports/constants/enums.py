from enum import IntEnum, StrEnum


class ExitCode(IntEnum):
    """Exit codes of the service process."""

    SUCCESS = 0
    FAILED = 1
    PROCESS_ERROR = 2


class ValidationErrorType(StrEnum):
    """Pydantic validation error types that have a specific cause text."""

    MISSING = "missing"
    STRING_TOO_SHORT = "string_too_short"
    EXTRA_FORBIDDEN = "extra_forbidden"
