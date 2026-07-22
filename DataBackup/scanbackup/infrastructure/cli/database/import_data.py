from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.application.use_case.database.import_data import DatabaseImportUseCase
from scanbackup.shared import Configuration, Terminal, Log


def import_data_to_database(collection: str, filepath: str, delimiter: str) -> None:
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

            use_case = DatabaseImportUseCase(database=MongoDatabase())
            use_case.execute(
                cfg_db=cfg_db,
                cfg_layers=cfg_layers,
                name_collection=collection,
                input_filepath=filepath,
                delimiter=delimiter,
            )
        except Exception:
            terminal.error("Importación de datos fallida")
            exit(1)
        else:
            terminal.info("Proceso finalizado con éxito")
