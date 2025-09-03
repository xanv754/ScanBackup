import click
from systemgrd.database.libs.database import DatabaseMongo
from systemgrd.utils import ConfigurationHandler, log


@click.group()
def cli():
    """SysGRD - Base de Datos.

    Interfaz de línea de comandos para el manejo de operaciones de la base
    de datos del sistema.
    """
    pass


@cli.command(help="Crea una nueva base de datos en MondoDB para el sistema.")
@click.option("--dev", is_flag=True, help="Carga las variables del entorno de desarrollo")
def start(dev: bool = False, test: bool = False):
    config = ConfigurationHandler(dev=dev, test=test)
    log.info("Inicialización de la base de datos...")
    uri_mongo = config.uri_mongo
    mongo_database = DatabaseMongo(uri=uri_mongo)
    mongo_status = mongo_database.initialize()
    if mongo_status: 
        log.info("Inicialización de la base de datos completada exitosamente")
    else:
        log.error("Inicialización de la base de datos fallida")


@cli.command(help="Destruye la base de datos en MondoDB con toda su información. Esta acción no se puede deshacer.")
@click.option("--dev", is_flag=True, help="Carga las variables del entorno de desarrollo")
def drop(dev: bool = False, test: bool = False):
    config = ConfigurationHandler(dev=dev, test=test)
    log.info("Inicio de la destrucción de la base de datos...")
    uri_mongo = config.uri_mongo
    mongo_database = DatabaseMongo(uri=uri_mongo)
    mongo_status = mongo_database.drop()
    if mongo_status:
        log.info("Destrucción de la base de datos completada exitosamente")
    else:
        log.error("Destrucción de la base de datos fallida")


if __name__ == "__main__":
    cli()
