from scanbackup.shared.errors.system import ScanBackupError


class SCANScannerError(ScanBackupError):
    def __init__(
        self, message: str | None = None, error: any = None, layer: str | None = None
    ) -> None:
        module = "SCAN Scanner"
        if not message:
            message = "Error en la ejecución de captura de tráfico de SCAN"
        if layer:
            message = message + f". Error en la capa: {layer}"
        super().__init__(module=module, message=message, error=error)


class SCANScannerConfigError(ScanBackupError):
    def __init__(self, error: any = None) -> None:
        module = "SCAN Scanner"
        message = "Fallo configuración para la captura de data"
        super().__init__(module=module, message=message, error=error)
