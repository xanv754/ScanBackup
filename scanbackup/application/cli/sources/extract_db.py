from pathlib import Path
from scanbackup.infrastructure import MongoTrafficSourceBBIPRepository
from scanbackup.application.use_case.bbip.updaters.source_traffic import (
    TrafficSourceUpdaterUseCase,
)
from scanbackup.shared import Configuration, Terminal, Log


def traffic_export_from_database(
    path: str | None = None, layer: str | None = None
) -> None:
    terminal = Terminal()

    message = "Exportando información de fuentes de tráfico para el BBIP"
    Log.info(message)
    terminal.info(message)

    with terminal.status("Configurando sistema...") as status:
        try:
            system = Configuration()
            cfg_layers = system.get_cfg_layers()
            if not path:
                dirpath = Path.home()
            else:
                dirpath = Path(path)
            repository = MongoTrafficSourceBBIPRepository()

            terminal.loading(status, "Exportando información...")

            process = TrafficSourceUpdaterUseCase(repository=repository, path=dirpath)
            if not layer:
                layers = cfg_layers.bbip.names
            else:
                layers = [layer]

            process.export(layers)
        except Exception:
            message = "Falla de exportación de las fuentes"
            terminal.error(message)
            Log.error(message)
        else:
            message = "Proceso finalizado con éxito"
            terminal.info(message)
            Log.info(message)
