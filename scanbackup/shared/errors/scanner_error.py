from scanbackup.shared.errors.system import ScanBackupError, ModuleSystem


class ScannerError(ScanBackupError):
    def __init__(
        self, message: str | None = None, error: any = None, layer: str | None = None
    ) -> None:
        module = ModuleSystem.SCANNER.value
        if not message:
            message = "Error en la ejecución de captura de tráfico de SCAN"
        if layer:
            message = message + f". Error en la capa: {layer}"
        super().__init__(module=module, message=message, error=error)


class ScannerConfigError(ScanBackupError):
    def __init__(self, error: any = None) -> None:
        module = ModuleSystem.SCANNER.value
        message = "Fallo configuración para la captura de data"
        super().__init__(module=module, message=message, error=error)
