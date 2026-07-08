from typing import Any
from scanbackup.shared.errors.system import ScanBackupError, ModuleSystem


class ConfigError(ScanBackupError):
    def __init__(
        self,
        message: str | None = None,
        error: Any = None,
    ) -> None:
        module = ModuleSystem.CONF
        if not message:
            message = "Error desconocido en la carga de la configuración"
        super().__init__(module=module, message=message, error=error)


class SchemaConfigError(ConfigError):
    def __init__(
        self,
        error: Any = None,
        extra_msg: str | None = None,
    ) -> None:
        message = "Error en el esquema de la configuración"
        if extra_msg:
            message = message + f". {extra_msg}"
        super().__init__(message=message, error=error)


class ValueConfigError(ConfigError):
    def __init__(
        self,
        error: Any = None,
        extra_msg: str | None = None,
    ) -> None:
        message = "Valores no válidos encontrados en la configuración"
        if extra_msg:
            message = message + f". {extra_msg}"
        super().__init__(message=message, error=error)


class LayerNotDefined(ConfigError):
    def __init__(self, layer_name: str, error: Any = None) -> None:
        message = f"La capa {layer_name} no fue encontrada en la configuración. No se pudo asociar a ningún esquema"
        super().__init__(message, error)
