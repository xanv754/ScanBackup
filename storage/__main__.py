import click
from storage.database.factory.mongo import MongoDatabaseFactory
from utils.config import ConfigurationHandler
from utils.log import LogHandler


@click.group()
def cli():
    """CPGRD Database

    CLI to controller database operations. Use with caution.
    """
    pass


@cli.command(help="Perfom database migrations.")
def migration():
    LogHandler.log("Starting migrations...", warn=True)
    config = ConfigurationHandler()
    uri = config.uri_mongo
    database = MongoDatabaseFactory().get_database(uri=uri)
    status_response = database.migration()
    database.close_connection()
    if status_response: 
        LogHandler.log("Migrations completed", info=True)
    else:
        LogHandler.log("Migrations failed", err=True)


@cli.command(help="Rollback database operations.")
def rollback():
    LogHandler.log("Starting rollback...", warn=True)
    config = ConfigurationHandler()
    uri = config.uri_mongo
    database = MongoDatabaseFactory().get_database(uri=uri)
    status_response = database.rollback()
    database.close_connection()
    if status_response: 
        LogHandler.log("Rollback completed", info=True)
    else:
        LogHandler.log("Rollback failed", err=True)


if __name__ == "__main__":
    cli()
