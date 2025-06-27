import click
from database.libs.factory.mongo import DatabaseMongoFactory
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
    mongo_database = DatabaseMongoFactory().get_database(uri=uri_mongo)
    mongo_status = mongo_database.initialize()
    if mongo_status: 
        log.info("Migrations successfully completed")
    else:
        log.error("Migrations completed not successfully")


@cli.command(help="Rollback database operations.")
def rollback():
    config = ConfigurationHandler()
    log.info("Starting rollback...")
    uri_mongo = config.uri_mongo
    mongo_database = DatabaseMongoFactory().get_database(uri=uri_mongo)
    mongo_status = mongo_database.drop()
    if mongo_status:
        log.info("Rollback successfully completed")
    else:
        log.error("Rollback completed not successfully")


if __name__ == "__main__":
    cli()
