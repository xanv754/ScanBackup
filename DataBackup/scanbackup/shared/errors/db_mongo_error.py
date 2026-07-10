from typing import Any
from scanbackup.shared.errors.system import ScanBackupError, ModuleSystem


class MongoDatabaseError(ScanBackupError):
    def __init__(self, message: str | None = None, error: Any = None) -> None:
        module = ModuleSystem.MONGO
        if not message:
            message = "Error desconocido al procesar operación"
        super().__init__(module=module, message=message, error=error)


class MongoCollectionNotFoundError(MongoDatabaseError):
    def __init__(self, name: str, error: Any = None) -> None:
        message = f"La colección {name} no fue encontrada en la base de datos"
        super().__init__(message=message, error=error)


class MongoCreateCollectionError(MongoDatabaseError):
    def __init__(self, name: str, error: Any = None) -> None:
        message = f"Error al crear la colección {name}"
        super().__init__(message=message, error=error)


class MongoExportCollectionError(MongoDatabaseError):
    def __init__(
        self, name: str, error: Any = None, extra_msg: str | None = None
    ) -> None:
        message = f"Error al exportar la data de la colección {name}"
        if extra_msg:
            message = message + f". {extra_msg}"
        super().__init__(message=message, error=error)


class MongoImportCollectionError(MongoDatabaseError):
    def __init__(self, name: str, error: Any = None) -> None:
        message = f"Error al importar la data en la colección {name}"
        super().__init__(message=message, error=error)


class MongoDeleteCollectionError(MongoDatabaseError):
    def __init__(self, name: str, error: Any = None) -> None:
        message = f"Error al borrar la data y eliminar la colección {name}"
        super().__init__(message=message, error=error)


class MongoConnectionError(MongoDatabaseError):
    def __init__(self, error: Any = None, extra_msg: str | None = None) -> None:
        message = "Error al conectarse a la base de datos"
        if extra_msg:
            message = message + f". {extra_msg}"
        super().__init__(message=message, error=error)


class MongoInsertFailedError(MongoDatabaseError):
    def __init__(self, extra_msg: str | None = None, error: Any = None) -> None:
        message = "Error al insertar nueva información"
        if extra_msg:
            message = message + f". {extra_msg}"
        super().__init__(message, error)


class MongoGetFailedError(MongoDatabaseError):
    def __init__(
        self, name_collection: str, extra_msg: str | None = None, error: Any = None
    ) -> None:
        message = f"No se pudo obtener información de la colección {name_collection}"
        if extra_msg:
            message = message + f". {extra_msg}"
        super().__init__(message=message, error=error)
