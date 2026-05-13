from scanbackup.shared.errors.exporters.base import ExportError


class ExcelExportError(ExportError):
    def __init__(self, filename: str | None = None, error: any = None) -> None:
        message = "Exportación del reporte a excel fallida"
        super().__init__(message=message, error=error, filename=filename)
