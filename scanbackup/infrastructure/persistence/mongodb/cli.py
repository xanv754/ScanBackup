import click
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.shared import URIEnvironment, Terminal, Log


@click.group()
def cli():
    """Administrador de la Base de Datos"""
    pass


@cli.command(help="Crea una nueva base de datos en MondoDB para el sistema.")
@click.option(
    "--dev", is_flag=True, help="Carga las variables del entorno de desarrollo"
)
def setup(dev: bool = False):
    terminal = Terminal()

    start_info = "Inicialización colecciones de la base de datos"
    Log.info(start_info)
    terminal.info(start_info)

    with terminal.status("Cargando configuración del sistema...") as status:
        try:
            config = URIEnvironment(dev=dev)
            uri_mongo = config.get_uri_db()

            terminal.loading(status, "Iniciando proceso...")

            mongo_database = MongoDatabase(uri=uri_mongo)
            mongo_database.initialize()
        except Exception:
            terminal.error("Inicialización de la base de datos fallida")
            exit(1)
        else:
            terminal.info("Proceso finalizado con éxito")


@cli.command(
    help="Eliminación de las colecciones. PRECAUCIÓN: esta acción no puede deshacerse una vez ejecutada"
)
@click.option(
    "--force",
    is_flag=True,
    help="Fuerza eliminación de las colecciones. ADVERTENCIA: esta acción no puede deshacerse una vez ejecutada",
)
@click.option(
    "--dev", is_flag=True, help="Carga las variables del entorno de desarrollo"
)
def drop(force: bool = False, dev: bool = False):
    terminal = Terminal()

    start_info = "Eliminación de colecciones de la base de datos"
    Log.info(start_info)
    terminal.info(start_info)

    with terminal.status("Cargando configuración del sistema...") as status:
        try:
            config = URIEnvironment(dev=dev)
            uri_mongo = config.get_uri_db()

            terminal.loading(status, "Iniciando proceso...")

            mongo_database = MongoDatabase(uri=uri_mongo)
            mongo_database.drop(force)
        except Exception:
            terminal.error("Eliminación de la base de datos fallida")
            exit(1)
        else:
            terminal.info("Proceso finalizado con éxito")


@cli.command("import", help="Importa datos de un archivo .csv a una colección.")
@click.option(
    "--file",
    type=click.Path(exists=True),
    required=True,
    help="Archivo .csv a importar",
)
@click.option(
    "--collection",
    type=click.Choice(MongoCollectionName),
    required=True,
    help="Colección a importar",
)
@click.option("--delimiter", help="Delimitador de campos")
@click.option(
    "--dev", is_flag=True, help="Carga las variables del entorno de desarrollo"
)
def import_data(
    file: str,
    collection: MongoCollectionName,
    delimiter: str | None = None,
    dev: bool = False,
) -> None:
    terminal = Terminal()

    start_info = f"Importación de datos a la colección {collection}"
    Log.info(start_info)
    terminal.info(start_info)

    with terminal.status("Cargando configuración del sistema...") as status:
        try:
            config = URIEnvironment(dev=dev)
            uri_mongo = config.get_uri_db()

            terminal.loading(status, "Iniciando proceso...")

            mongo_database = MongoDatabase(uri=uri_mongo)
            mongo_database.import_data(
                name_collection=collection, filepath=file, delimiter=delimiter
            )
        except Exception:
            terminal.error("Importación de datos fallida")
            exit(1)
        else:
            terminal.info("Proceso finalizado con éxito")


@cli.command(
    "export", help="Exporta todos los datos de una colección a un archivo .csv."
)
@click.option(
    "--dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directorio de exportación",
)
@click.option(
    "--collection",
    type=click.Choice(MongoCollectionName),
    help="Colección a importar",
)
@click.option("--delimiter", help="Delimitador de campos")
@click.option(
    "--id",
    is_flag=True,
    help="Incluir ObjectID de registros en la exportación. Por defecto True",
)
@click.option(
    "--dev", is_flag=True, help="Carga las variables del entorno de desarrollo"
)
def export_data(
    collection: MongoCollectionName | None,
    dir: str | None = None,
    delimiter: str | None = None,
    id: bool = True,
    dev: bool = False,
) -> None:
    terminal = Terminal()

    start_info = f"Exportación de datos de la colección {collection}"
    Log.info(start_info)
    terminal.info(start_info)

    with terminal.status("Cargando configuración del sistema...") as status:
        try:
            config = URIEnvironment(dev=dev)
            uri_mongo = config.get_uri_db()

            terminal.loading(status, "Iniciando proceso...")

            mongo_database = MongoDatabase(uri=uri_mongo)
            mongo_database.export_data(
                dirpath=dir,
                name_collection=collection,
                delimiter=delimiter,
                include_id=id,
            )
        except Exception:
            terminal.error("Exportación de datos fallida")
            exit(1)
        else:
            terminal.info("Proceso finalizado con éxito")


if __name__ == "__main__":
    cli()
