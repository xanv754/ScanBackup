from pathlib import Path
from scanbackup.infrastructure import MongoTrafficSourceBBIPRepository
from scanbackup.application.use_case.bbip.updaters.source_traffic import (
    UpdateBBIPSources,
)
from scanbackup.shared import Configuration, Terminal, Log


def traffic_export_from_database(
    dirpath: str | None = None, layer: str | None = None
) -> None:
    terminal = Terminal()

    message = "Exportando información de fuentes de tráfico para el BBIP"
    Log.info(message)
    terminal.info(message)

    with terminal.status("Configurando sistema...") as status:
        try:
            system = Configuration()
            cfg_layers = system.get_cfg_layers()
            dirpath = Path(dirpath)
            repository = MongoTrafficSourceBBIPRepository()

            terminal.loading(status, "Exportando información...")

            process = UpdateBBIPSources(repository=repository, path=dirpath)
            if not layer:
                layers = cfg_layers.bbip.names
            else:
                layers = layers[layer]

            process.export(layers)
        except Exception:
            terminal.error("Falla de exportación de las fuentes")
        else:
            terminal.info("Proceso finalizado con éxito")
