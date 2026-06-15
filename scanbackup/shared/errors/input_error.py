from typing import Any
from pathlib import Path
from scanbackup.shared.errors.system import ModuleSystem
from scanbackup.shared.outputs.terminal import Terminal
from scanbackup.shared.outputs.logs import Log


class FileEmptyError(Exception):
    def __init__(self, filepath: str) -> None:
        module = ModuleSystem.INPUT.value
        message = f"El contenido del archivo {filepath} está vacío o no se encontró ninguna data válida"
        self.message = message
        Log.warning(self.message)
        Terminal.warning(preffix=module, message=self.message)
        super().__init__()

    def __str__(self) -> str:
        return self.message


class FileExtensionError(Exception):
    def __init__(self, filepath: str) -> None:
        module = ModuleSystem.INPUT.value
        message = f"Extensión del archivo {filepath} no válida"
        self.message = message
        Log.warning(self.message)
        Terminal.warning(preffix=module, message=self.message)
        super().__init__()

    def __str__(self) -> str:
        return self.message


class ContentFileError(Exception):
    def __init__(
        self, filepath: str, message: str | None = None, error: Any = None
    ) -> None:
        self.module = ModuleSystem.INPUT.value
        if not message:
            message = f"La entrada del archivo {filepath} no es la correcta. Puede que le falte información"
        if error:
            message = message + ".\n" + str(error)
        self.message = message
        Log.warning(self.message)
        Terminal.error(preffix=self.module, message=self.message)
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class DataNotFoundError(Exception):
    def __init__(self, filepath: str | Path) -> None:
        self.module = ModuleSystem.INPUT.value
        if type(filepath) is Path:
            filepath = str(filepath.resolve())
        message = f"No existe el directorio o archivo en {filepath}"
        self.message = message
        Log.warning(self.message)
        Terminal.error(preffix=self.module, message=self.message)
        super().__init__(self.message)
