import click
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.shared import Configuration, Terminal, Log


@click.group()
def cli():
    """Administrador de la Base de Datos"""
    pass


@cli.command(
    help="Crea todas las colecciones especificadas en la configuración del sistema."
)
def setup():
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

            database = MongoDatabase()
            database.set_uri(cfg_db)
            database.create_collections(config=cfg_layers)
        except Exception:
            terminal.error("Inicialización de la base de datos fallida")
            exit(1)
        else:
            terminal.info("Proceso finalizado con éxito")


@cli.command(
    help="Ver nombres de las colecciones actualmente existentes en la base de datos."
)
def inspect() -> None:
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


@cli.command("import", help="Importa la data de un archivo .csv a una colección.")
@click.option(
    "--collection",
    required=True,
    help="Nombre de la colección de la base de datos a la que se quiere importar los datos.",
)
@click.option(
    "--filepath",
    type=click.Path(exists=True),
    required=True,
    help="Ruta del archivo .csv a importar.",
)
@click.option("--delimiter", required=False, help="Delimitador de campos del archivo.")
def import_data(collection: str, filepath: str, delimiter: str | None = None) -> None:
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


@cli.command("export", help="Exporta la data de colección en un archivo .csv.")
@click.option(
    "--collection",
    required=True,
    help="Nombre de la colección de la base de datos a la que se quiere exportar los datos.",
)
@click.option(
    "--dirpath",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Ruta de la carpeta a exportar la data.",
)
@click.option("--delimiter", required=False, help="Delimitador de campos del archivo.")
@click.option("--id", is_flag=True, required=False, help="Incluir el ID en el archivo.")
def export_data(
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

            database = MongoDatabase()
            database.set_uri(cfg_db)
            filepath_export = database.export_data(
                config=cfg_layers,
                name_collection=collection,
                dirpath=dirpath,
                delimiter=delimiter,
                include_id=id,
            )
        except Exception:
            terminal.error("Exportación de datos fallida")
            exit(1)
        else:
            terminal.info(
                f"Proceso finalizado con éxito. Archivo exportado en {filepath_export}"
            )


if __name__ == "__main__":
    cli()
