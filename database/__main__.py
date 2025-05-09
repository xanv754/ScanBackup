import click
from database.libs.factory.mongo import MongoDatabaseFactory
from database.libs.factory.postgres import PostgresDatabaseFactory
from utils.config import ConfigurationHandler
from utils.log import log


@click.group()
def cli():
    """CPGRD Database

    CLI to controller database operations. Use with caution.
    """
    pass


@cli.command(help="Perfom database migrations.")
def migration():
    config = ConfigurationHandler()
    log.info("Starting migrations...")
    uri_mongo = config.uri_mongo
    uri_postgres = config.uri_postgres
    mongo_status = False
    postgres_status = False
    mongo_database = MongoDatabaseFactory().get_database(uri=uri_mongo)
    if mongo_database.connected:
        mongo_status = mongo_database.migration()
        mongo_database.close_connection()
    postgres_database = PostgresDatabaseFactory().get_database(uri=uri_postgres)
    if postgres_database.connected:
        postgres_status = postgres_database.migration()
        postgres_database.close_connection()
    if mongo_status and postgres_status: 
        log.info("Migrations successfully completed")
    else:
        log.error("Migrations completed not successfully")


@cli.command(help="Rollback database operations.")
def rollback():
    config = ConfigurationHandler()
    log.info("Starting rollback...")
    uri_mongo = config.uri_mongo
    uri_postgres = config.uri_postgres
    mongo_database = MongoDatabaseFactory().get_database(uri=uri_mongo)
    mongo_status = mongo_database.rollback()
    mongo_database.close_connection()
    postgres_database = PostgresDatabaseFactory().get_database(uri=uri_postgres)
    postgres_status = postgres_database.rollback()
    postgres_database.close_connection()
    if mongo_status and postgres_status:
        log.info("Rollback successfully completed")
    else:
        log.error("Rollback completed not successfully")


if __name__ == "__main__":
    cli()
