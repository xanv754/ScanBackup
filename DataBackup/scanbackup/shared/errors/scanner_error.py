from typing import Any
from scanbackup.shared.errors.system import ScanBackupError, ModuleSystem


class ScannerError(ScanBackupError):
    def __init__(
        self, message: str | None = None, error: Any = None, layer: str | None = None
    ) -> None:
        module = ModuleSystem.SCANNER
        if not message:
            message = "Error en la ejecución de captura de tráfico de SCAN"
        if layer:
            message = message + f". Error en la capa: {layer}"
        super().__init__(module=module, message=message, error=error)
