from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.shared import Configuration, Terminal, Log


def get_collection_names() -> None:
    terminal = Terminal()

    start_info = "Colecciones datos a la base de datos:"
    Log.info(start_info)
    terminal.info(start_info)

    with terminal.status("Cargando configuración del sistema...") as status:
        try:
            config = Configuration()
            cfg_db = config.get_cfg_database()

            terminal.loading(status, "Inspeccionando colecciones...")

            database = MongoDatabase()
            database.set_uri(cfg_db)
            collections = database.get_collection_names()
            terminal.list(collections)
        except Exception:
            terminal.error("Proceso fallido. Sin búsqueda")
            exit(1)
