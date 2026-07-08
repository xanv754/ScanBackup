from enum import Enum
from typing import Any
from scanbackup.shared.outputs.logs import Log
from scanbackup.shared.outputs.terminal import Terminal


class ModuleSystem(str, Enum):
    CONF = "Configuración"
    SCANNER = "SCAN Scanner"
    DATABASE = "Database"
    MONGO = "Mongo Database"
    REPORT = "Reporte"
    INPUT = "IO"
    UPDATER = "Data Actualizador"


class ScanBackupError(Exception):
    def __init__(
        self, message: str, error: Any = None, module: ModuleSystem | None = None
    ) -> None:
        if error:
            message = message + ".\n" + str(error)
        self.error = error
        if not module:
            self.module = "System"
        else:
            self.module = module.value
        self.message = message
        Log.error(message)
        Terminal.error(preffix=self.module, message=self.message)
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.message}"
