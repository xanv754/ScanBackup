from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.shared import Configuration, Terminal, Log


def import_data_to_database(
    collection: str, filepath: str, delimiter: str | None = None
) -> None:
    terminal = Terminal()

    start_info = "Importando datos a la base de datos"
    Log.info(start_info)
    terminal.info(start_info)

    with terminal.status("Cargando configuración del sistema...") as status:
        try:
            config = Configuration()
            cfg_db = config.get_cfg_database()
            cfg_layers = config.get_cfg_layers()

            terminal.loading(status, "Iniciando proceso...")

            database = MongoDatabase()
            database.set_uri(cfg_db)
            database.import_data(
                name_collection=collection,
                config=cfg_layers,
                filepath=filepath,
                delimiter=delimiter,
            )
        except Exception:
            terminal.error("Importación de datos fallida")
            exit(1)
        else:
            terminal.info("Proceso finalizado con éxito")
