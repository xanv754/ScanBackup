from typing import Any
from scanbackup.shared.errors.system import ScanBackupError, ModuleSystem


class UpdaterError(ScanBackupError):
    def __init__(
        self, message: str | None = None, error: Any = None, layer: str | None = None
    ) -> None:
        module = ModuleSystem.UPDATER
        if not message:
            message = "Error en la actualización de datos del sistema"
        if layer:
            message = message + f". Error en la capa: {layer}"
        super().__init__(module=module, message=message, error=error)
