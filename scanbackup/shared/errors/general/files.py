from scanbackup.shared.outputs.terminal import Terminal
from scanbackup.shared.outputs.logs import Log


class FileEmptyError(Exception):
    def __init__(self, filepath: str, module: str | None = None) -> None:
        message = f"Archivo {filepath} vacío"
        if module:
            message = module + ": " + message
        self.message = message
        Log.warning(self.message)
        Terminal.warning(preffix=module, message=self.message)
        super().__init__()

    def __str__(self) -> str:
        return self.message
