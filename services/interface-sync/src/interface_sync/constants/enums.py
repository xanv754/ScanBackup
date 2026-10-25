from enum import StrEnum


class LogEvent(StrEnum):
    """Messages shared by the log and the terminal for the same event."""

    PROCESS_ERROR = "Error general del proceso"
    INVALID_CONFIG = "Configuración inválida"
    CONFIG_LOADED = "Configuración cargada"
    PAGE_SUCCEEDED = "Página exitosa"
    PAGE_FAILED = "Página fallida"
    GENERAL_SUCCEEDED = "Resultado general exitoso"
    GENERAL_FAILED = "Resultado general fallido"
    INCOMPLETE_INTERFACE = "Interfaz incompleta"
    DEFAULT_CAPACITY = "Capacidad por defecto"


class TerminalLevel(StrEnum):
    """Levels printed by the terminal."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationErrorType(StrEnum):
    """Pydantic validation error types that `ConfigurationFile` translates."""

    MISSING = "missing"
    STRING_TOO_SHORT = "string_too_short"
    EXTRA_FORBIDDEN = "extra_forbidden"
    STRING_TYPE = "string_type"
    VALUE_ERROR = "value_error"
    MODEL_TYPE = "model_type"
