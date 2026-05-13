from scanbackup.shared.outputs.logs import Log
from scanbackup.shared.outputs.terminal import Terminal


class ScanBackupError(Exception):
    def __init__(
        self, message: str, error: any = None, module: str | None = None
    ) -> None:
        if error:
            message = message + ".\n" + str(error)
        self.error = error
        if not module:
            self.module = "System"
        else:
            self.module = module
        self.message = message
        Log.error(message)
        Terminal.error(preffix=self.module, message=self.message)
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.message}"
