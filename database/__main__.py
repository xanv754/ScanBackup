import os
import click
from dotenv import load_dotenv
from database.libs.factory.mongo import MongoDatabaseFactory
from database.libs.factory.postgres import PostgresDatabaseFactory
from utils.config import ConfigurationHandler
from utils.log import LogHandler


load_dotenv(override=True)
log = LogHandler()


@click.group()
def cli():
    """CPGRD Database

    CLI to controller database operations. Use with caution.
    """
    pass


@cli.command(help="Perfom database migrations.")
@click.option("--test", is_flag=True, help="Realize migrations in the test database.")
def migration(test: bool):
    config = ConfigurationHandler()
    if test:
        log.export("Starting migrations in test mode...", warn=True)
        uri_test_mongo = os.getenv("URI_TEST_MONGO")
        if not uri_test_mongo:
            log.export("URI test MongoDB variable not found in enviroment file.", err=True)
            exit(1)
        uri_test_postgres = os.getenv("URI_TEST_POSTGRES")
        if not uri_test_postgres:
            log.export("URI test PostgreSQL variable not found in enviroment file.", err=True)
            exit(1)
        config.set_uri(uri_postgres=uri_test_postgres, uri_mongo=uri_test_mongo)
    else:
        log.export("Starting migrations...", warn=True)
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
        log.export("Migrations successfully completed", info=True)
    else:
        log.export("Migrations completed not successfully", err=True)


@cli.command(help="Rollback database operations.")
@click.option("--test", is_flag=True, help="Realize rollback in the test database.")
def rollback(test: bool):
    config = ConfigurationHandler()
    if test:
        log.export("Starting rollback in test mode...", warn=True)
        uri_test_mongo = os.getenv("URI_TEST_MONGO")
        if not uri_test_mongo:
            log.export("URI test MongoDB variable not found in enviroment file.", err=True)
            exit(1)
        uri_test_postgres = os.getenv("URI_TEST_POSTGRES")
        if not uri_test_postgres:
            log.export("URI test PostgreSQL variable not found in enviroment file.", err=True)
            exit(1)
        config.set_uri(uri_postgres=uri_test_postgres, uri_mongo=uri_test_mongo)
    else:
        log.export("Starting rollback...", warn=True)
    uri_mongo = config.uri_mongo
    uri_postgres = config.uri_postgres
    mongo_database = MongoDatabaseFactory().get_database(uri=uri_mongo)
    mongo_status = mongo_database.rollback()
    mongo_database.close_connection()
    postgres_database = PostgresDatabaseFactory().get_database(uri=uri_postgres)
    postgres_status = postgres_database.rollback()
    postgres_database.close_connection()
    if mongo_status and postgres_status:
        log.export("Rollback successfully completed", info=True)
    else:
        log.export("Rollback completed not successfully", err=True)


if __name__ == "__main__":
    cli()
