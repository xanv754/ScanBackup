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


class SampleCountVerdict(StrEnum):
    """Result of comparing the samples of a day with the expected amount."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    EXCESS = "excess"
    EMPTY = "empty"


class FailureCause(StrEnum):
    """Why an interface failed. The value is the text reported to the operator."""

    TIMEOUT = "tiempo de espera agotado"
    UNREACHABLE = "sin conexión a SCAN"
    UNAUTHORIZED = "credenciales rechazadas"
    HTTP_ERROR = "error de SCAN"
    EMPTY_RESPONSE = "respuesta sin datos"
    NO_VALID_SAMPLES = "sin muestras válidas del día anterior"
    STORAGE_ERROR = "error de base de datos al almacenar"


class InterfaceStatus(StrEnum):
    """Status of an interface in the `interfaces` collection."""

    ACTIVE = "activa"
    DECOMMISSIONED = "desincorporada"


class CutReason(StrEnum):
    """Why the processing of a layer was cut before finishing [RF-027]."""

    CONSECUTIVE_FAILURES = "fallas consecutivas"
    STORAGE_ERROR = "error de base de datos al almacenar"
