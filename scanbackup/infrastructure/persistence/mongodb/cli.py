import click
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
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

            terminal.loading(status, "Creando colecciones...")

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

            terminal.loading(status, "Eliminando colecciones...")

            mongo_database = MongoDatabase(uri=uri_mongo)
            mongo_database.drop(force)
        except Exception:
            terminal.error("Eliminación de la base de datos fallida")
            exit(1)
        else:
            terminal.info("Proceso finalizado con éxito")


if __name__ == "__main__":
    cli()
