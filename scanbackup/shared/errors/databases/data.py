from scanbackup.shared.errors.system import ScanBackupError


class DataImportError(ScanBackupError):
    def __init__(self, extra_msg: str | None = None, error: any = None) -> None:
        module = "Database"
        message = "Error al importar data a la base de datos"
        if extra_msg:
            message = message + f". {extra_msg}"
        super().__init__(module=module, message=message, error=error)


class DatabaseDataNotFoundError(DataImportError):
    def __init__(self, filepath: str, error: any = None) -> None:
        message = "Archivo"
        if filepath:
            message = message + filepath
        message = "no encontrado"
        super().__init__(extra_msg=message, error=error)


class DatabaseDataContentError(DataImportError):
    def __init__(self, error: any = None, extra_msg: str | None = None) -> None:
        message = "Contenido del archivo inválido"
        if extra_msg:
            message = message + f". {extra_msg}"
        super().__init__(error=error)
