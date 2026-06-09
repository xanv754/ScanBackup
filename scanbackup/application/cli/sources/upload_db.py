from pathlib import Path
from scanbackup.infrastructure import MongoTrafficSourceBBIPRepository
from scanbackup.application.use_case.bbip.updaters.source_traffic import (
    UpdateBBIPSources,
)
from scanbackup.shared import Terminal, Log


def traffic_upload_to_database(filepath: str) -> None:
    terminal = Terminal()

    message = "Actualizando de información de archivos fuentes de tráfico para el BBIP"
    Log.info(message)
    terminal.info(message)

    with terminal.status("Configurando sistema...") as status:
        try:
            filepath = Path(filepath)
            repository = MongoTrafficSourceBBIPRepository()

            terminal.loading(status, "Procesando información...")

            process = UpdateBBIPSources(repository=repository, path=filepath)
            process.upload()
        except Exception:
            terminal.error("Falla de actualización de los archivos fuentes")
        else:
            terminal.info("Proceso finalizado con éxito")
