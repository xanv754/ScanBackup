from scanbackup.shared.errors.system import ScanBackupError


class EnvConfigError(ScanBackupError):
    def __init__(self, message: str | None = None, error: any = None) -> None:
        module = "Environment"
        if not message:
            message = "Error en la lectura de variables de entorno del sistema"
        super().__init__(module=module, message=message, error=error)


class EnvFileNotFoundError(EnvConfigError):
    def __init__(self, error: any = None) -> None:
        message = "Archivo con variables de entorno no encontrado"
        super().__init__(message=message, error=error)


class MissingEnvironmentVariableError(EnvConfigError):
    def __init__(self, var_name: str | None = None, error: any = None) -> None:
        message = "Variables de entorno no encontrado"
        if var_name:
            message = message + f". Variable faltante: {var_name}"
        super().__init__(message=message, error=error)
