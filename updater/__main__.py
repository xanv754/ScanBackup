import click
from updater.handler.borde import BordeUpdaterHandler
from updater.handler.bras import BrasUpdaterHandler
from updater.handler.caching import CachingUpdaterHandler
from updater.handler.rai import RaiUpdaterHandler
from utils.log import log


@click.group
def cli():
    """CLI Updater Database"""
    pass


@cli.command(help="Upload data obtained to database")
@click.option("--date", required=False, help="Date to upload data. Format YYYY-MM-DD")
def data(date: str):
    try:
        log.info("Starting updater borde data...")
        borderHandler = BordeUpdaterHandler()
        if date:
            data_borde = borderHandler.get_data(date=date)
        else:
            data_borde = borderHandler.get_data()
        borderHandler.load_data(data=data_borde)
    except Exception as e:
        log.error(f"Borde data upload failed. {e}")
    finally:
        log.info("Updater borde data finished")
    try:
        log.info("Starting updater bras data...")
        brasHandler = BrasUpdaterHandler()
        if date:
            data_borde = brasHandler.get_data(date=date)
        else:
            data_borde = brasHandler.get_data()
        brasHandler.load_data(data=data_borde)
    except Exception as e:
        log.error(f"Bras data upload failed. {e}")
    finally:
        log.info("Updater bras data finished")
    try:
        log.info("Starting updater caching data...")
        cachingHandler = CachingUpdaterHandler()
        if date:
            data_borde = cachingHandler.get_data(date=date)
        else:
            data_borde = cachingHandler.get_data()
        cachingHandler.load_data(data=data_borde)
    except Exception as e:
        log.error(f"Caching data upload failed. {e}")
    finally:
        log.info("Updater caching data finished")
    try:
        log.info("Starting updater rai data...")
        raiHandler = RaiUpdaterHandler()
        if date:
            data_borde = raiHandler.get_data(date=date)
        else:
            data_borde = raiHandler.get_data()
        raiHandler.load_data(data=data_borde)
    except Exception as e:
        log.error(f"Rai data upload failed. {e}")
    finally:
        log.info("Updater rai data finished")


if __name__ == "__main__":
    cli()
