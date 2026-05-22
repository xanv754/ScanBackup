from scanbackup.shared.errors.system import ModuleSystem
from scanbackup.shared.outputs.terminal import Terminal
from scanbackup.shared.outputs.logs import Log


class FileEmptyError(Exception):
    def __init__(self, filepath: str) -> None:
        module = ModuleSystem.INPUT.value
        message = f"{module}: Archivo {filepath} vacío"
        self.message = message
        Log.warning(self.message)
        Terminal.warning(preffix=module, message=self.message)
        super().__init__()

    def __str__(self) -> str:
        return self.message


class FileExtensionError(Exception):
    def __init__(self, filepath: str) -> None:
        module = ModuleSystem.INPUT.value
        message = f"{module}: Extensión del archivo {filepath} no válida"
        self.message = message
        Log.warning(self.message)
        Terminal.warning(preffix=module, message=self.message)
        super().__init__()

    def __str__(self) -> str:
        return self.message
