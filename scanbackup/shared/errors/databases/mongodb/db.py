from scanbackup.shared.errors.system import ScanBackupError


class MongoDatabaseError(ScanBackupError):
    def __init__(self, message: str | None = None, error: any = None) -> None:
        module = "Mongo Database"
        if not message:
            message = "Error desconocido al procesar operación"
        super().__init__(module=module, message=message, error=error)


class CreateCollectionMongoError(MongoDatabaseError):
    def __init__(self, name: str, error: any = None) -> None:
        message = f"Error al crear la colección {name}"
        super().__init__(message=message, error=error)


class ExportCollectionMongoError(MongoDatabaseError):
    def __init__(self, name: str, error: any = None) -> None:
        message = f"Error al exportar la data de la colección {name}"
        super().__init__(message=message, error=error)


class ImportCollectionMongoError(MongoDatabaseError):
    def __init__(self, name: str, error: any = None) -> None:
        message = f"Error al importar la data en la colección {name}"
        super().__init__(message=message, error=error)


class DeleteCollectionMongoError(MongoDatabaseError):
    def __init__(self, name: str, error: any = None) -> None:
        message = f"Error al borrar la data y eliminar la colección {name}"
        super().__init__(message=message, error=error)
