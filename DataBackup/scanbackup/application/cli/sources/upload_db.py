from pathlib import Path
from scanbackup.infrastructure import MongoTrafficSourceBBIPRepository
from scanbackup.application.use_case.bbip.updaters.source_traffic import (
    TrafficSourceUpdaterUseCase,
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

            process = TrafficSourceUpdaterUseCase(repository=repository, path=filepath)
            process.execute()
        except Exception:
            message = "Falla de actualización de los archivos fuentes"
            terminal.error(message)
            Log.error(message)
        else:
            message = "Proceso finalizado con éxito"
            terminal.info(message)
            Log.info(message)
