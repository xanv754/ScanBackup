from pathlib import Path
from scanbackup.infrastructure import (
    MongoTrafficSourceBBIPRepository,
    MongoIPSourceBBIPRepository,
    TrafficSourceBBIPReader,
    IPSourceBBIPReader,
    CSVWriter,
)
from scanbackup.application import (
    TrafficSourceUpdaterUseCase,
    IPSourceUpdaterUseCase,
)
from scanbackup.shared import Terminal, Log


def traffic_upload_to_database(file: str) -> None:
    terminal = Terminal()

    message = "Actualizando de información de archivos fuentes de tráfico para el BBIP"
    Log.info(message)
    terminal.info(message)

    with terminal.status("Configurando sistema...") as status:
        try:
            filepath = Path(file)
            repository = MongoTrafficSourceBBIPRepository()

            terminal.loading(status, "Procesando información...")

            process = TrafficSourceUpdaterUseCase(
                repository=repository,
                path=filepath,
                reader=TrafficSourceBBIPReader(),
                writer_factory=CSVWriter,
            )
            process.execute()
        except Exception:
            message = "Falla de actualización de los archivos fuentes"
            terminal.error(message)
            Log.error(message)
        else:
            message = "Proceso finalizado con éxito"
            terminal.info(message)
            Log.info(message)


def ip_upload_to_database(file: str) -> None:
    terminal = Terminal()

    message = "Actualizando de información de archivos fuentes de IP para el BBIP"
    Log.info(message)
    terminal.info(message)

    with terminal.status("Configurando sistema...") as status:
        try:
            filepath = Path(file)
            repository = MongoIPSourceBBIPRepository()

            terminal.loading(status, "Procesando información...")

            process = IPSourceUpdaterUseCase(
                repository=repository,
                path=filepath,
                reader=IPSourceBBIPReader(),
                writer_factory=CSVWriter,
            )
            process.execute()
        except Exception:
            message = "Falla de actualización de los archivos fuentes"
            terminal.error(message)
            Log.error(message)
        else:
            message = "Proceso finalizado con éxito"
            terminal.info(message)
            Log.info(message)
