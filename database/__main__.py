import click
from database.libs.factory.mongo import DatabaseMongoFactory
from utils.config import ConfigurationHandler
from utils.log import log


@click.group()
def cli():
    """SysGRD - Base de Datos.

    Interfaz de línea de comandos para el manejo de operaciones de la base
    de datos del sistema.
    """
    pass


@cli.command(help="Crea una nueva base de datos en MondoDB para el sistema.")
def start():
    config = ConfigurationHandler()
    log.info("Inicialización de la base de datos...")
    uri_mongo = config.uri_mongo
    mongo_database = DatabaseMongoFactory().get_database(uri=uri_mongo)
    mongo_status = mongo_database.initialize()
    if mongo_status: 
        log.info("Inicialización de la base de datos completada exitosamente")
    else:
        log.error("Inicialización de la base de datos fallida")


@cli.command(help="Destruye la base de datos en MondoDB con toda su información. Esta acción no se puede deshacer.")
def drop():
    config = ConfigurationHandler()
    log.info("Inicio de la destrucción de la base de datos...")
    uri_mongo = config.uri_mongo
    mongo_database = DatabaseMongoFactory().get_database(uri=uri_mongo)
    mongo_status = mongo_database.drop()
    if mongo_status:
        log.info("Destrucción de la base de datos completada exitosamente")
    else:
        log.error("Destrucción de la base de datos fallida")


if __name__ == "__main__":
    cli()
