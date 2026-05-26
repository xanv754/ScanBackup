from scanbackup.shared.errors.system import ScanBackupError, ModuleSystem


class ExportError(ScanBackupError):
    def __init__(
        self, message: str | None = None, error: any = None, filename: str | None = None
    ) -> None:
        module = ModuleSystem.REPORT.value
        if not message:
            message = "Error en la exportación de reporte"
        if filename:
            message = message + f". Reporte fallido: {filename}"
        super().__init__(module=module, message=message, error=error)


class ExcelExportError(ExportError):
    def __init__(self, filename: str | None = None, error: any = None) -> None:
        message = "Exportación de archivo a excel fallida"
        super().__init__(message=message, error=error, filename=filename)


class CSVExportError(ExportError):
    def __init__(self, filename: str | None = None, error: any = None) -> None:
        message = "Exportación de archivo .csv fallida"
        super().__init__(message=message, error=error, filename=filename)
