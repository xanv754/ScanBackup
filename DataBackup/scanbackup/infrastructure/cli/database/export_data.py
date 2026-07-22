from pathlib import Path
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.application.use_case.database.export_data import DatabaseExportUseCase
from scanbackup.shared import Configuration, Terminal, Log


def export_data_from_database(
    collection: str,
    dirpath: str,
    delimiter: str | None = None,
    id: bool = False,
) -> None:
    terminal = Terminal()

    start_info = "Exportando datos a la base de datos"
    Log.info(start_info)
    terminal.info(start_info)

    with terminal.status("Cargando configuración del sistema...") as status:
        try:
            config = Configuration()
            cfg_db = config.get_cfg_database()
            cfg_layers = config.get_cfg_layers()

            terminal.loading(status, "Iniciando proceso...")

            use_case = DatabaseExportUseCase(database=MongoDatabase())
            filepath_export = use_case.execute(
                cfg_db=cfg_db,
                cfg_layers=cfg_layers,
                name_collection=collection,
                dirpath=Path(dirpath),
                include_id=id,
            )
        except Exception:
            terminal.error("Exportación de datos fallida")
            exit(1)
        else:
            terminal.info(
                f"Proceso finalizado con éxito. Archivo exportado en {filepath_export}"
            )
