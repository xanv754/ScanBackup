from scanbackup.shared.errors.system import ScanBackupError, ModuleSystem


class DatabaseError(ScanBackupError):
    def __init__(self, message: str | None = None, error: any = None) -> None:
        module = ModuleSystem.DATABASE.value
        if not message:
            message = "Error desconocido en procesamiento de base de datos"
        super().__init__(module=module, message=message, error=error)


class DataImportError(DatabaseError):
    def __init__(self, extra_msg: str | None = None, error: any = None) -> None:
        message = "Error al importar data a la base de datos"
        if extra_msg:
            message = message + f". {extra_msg}"
        super().__init__(message=message, error=error)


class FileImportNotFoundError(DataImportError):
    def __init__(self, filepath: str, error: any = None) -> None:
        message = "Archivo"
        if filepath:
            message = message + filepath
        message = "no encontrado"
        super().__init__(extra_msg=message, error=error)


class DataContentError(DataImportError):
    def __init__(self, error: any = None, extra_msg: str | None = None) -> None:
        message = "Contenido del archivo inválido"
        if extra_msg:
            message = message + f". {extra_msg}"
        super().__init__(error=error)
