from enum import StrEnum


class InterfaceStatus(StrEnum):
    """Lifecycle status of a stored interface; interfaces are never deleted."""

    ACTIVE = "activa"
    DECOMMISSIONED = "desincorporada"


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
    INTERFACE_UPDATED = "Interfaz actualizada"
    STATUS_CHANGED = "Cambio de estatus"
    PAGE_SUMMARY = "Resumen de página"
    LAYER_SUMMARY = "Resumen de capa"
    LAYER_SKIPPED = "Capa sin desincorporación"
    DATABASE_FAILED = "Base de datos fallida"
    DUPLICATED_INTERFACE = "Interfaz duplicada en otra página"
    DATABASE_READY = "Base de datos disponible"
    SCRAPING_SUCCEEDED = "Scraping exitoso"


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
