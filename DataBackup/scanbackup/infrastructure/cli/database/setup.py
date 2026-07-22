from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.application.use_case.database.setup import DatabaseSetupUseCase
from scanbackup.shared import Configuration, Terminal, Log


def setup_database():
    terminal = Terminal()

    start_info = "Inicialización colecciones en la base de datos"
    Log.info(start_info)
    terminal.info(start_info)

    with terminal.status("Cargando configuración del sistema...") as status:
        try:
            config = Configuration()
            cfg_db = config.get_cfg_database()
            cfg_layers = config.get_cfg_layers()

            terminal.loading(status, "Iniciando proceso...")

            use_case = DatabaseSetupUseCase(database=MongoDatabase())
            use_case.execute(cfg_db=cfg_db, cfg_layers=cfg_layers)
        except Exception:
            terminal.error("Inicialización de la base de datos fallida")
            exit(1)
        else:
            terminal.info("Proceso finalizado con éxito")
