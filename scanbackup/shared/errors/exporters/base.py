from scanbackup.shared.errors.system import ScanBackupError


class ExportError(ScanBackupError):
    def __init__(
        self, message: str | None = None, error: any = None, filename: str | None = None
    ) -> None:
        module = "Exportation"
        if not message:
            message = "Error en la exportación de reporte"
        if filename:
            message = message + f". Reporte fallido: {filename}"
        super().__init__(module=module, message=message, error=error)
