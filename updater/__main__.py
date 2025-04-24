import click
from updater.handler.borde import BordeUpdaterHandler
from updater.handler.bras import BrasUpdaterHandler
from updater.handler.caching import CachingUpdaterHandler
from updater.handler.rai import RaiUpdaterHandler
from utils.log import LogHandler


log = LogHandler()


@click.group
def cli():
    """CLI Updater Database"""
    pass


@cli.command(help="Upload data obtained to database")
@click.option("--date", required=False, help="Date to upload data. Format YYYY-MM-DD")
def data(date: str):
    try:
        log.export("Starting updater borde data...", warn=True)
        borderHandler = BordeUpdaterHandler()
        if date:
            data_borde = borderHandler.get_data(date=date)
        else:
            data_borde = borderHandler.get_data()
        borderHandler.load_data(data=data_borde)
    except Exception as e:
        log.export(f"Borde data upload failed. {e}", err=True)
    finally:
        log.export("Updater borde data finished", info=True)
    try:
        log.export("Starting updater bras data...", warn=True)
        brasHandler = BrasUpdaterHandler()
        if date:
            data_borde = brasHandler.get_data(date=date)
        else:
            data_borde = brasHandler.get_data()
        brasHandler.load_data(data=data_borde)
    except Exception as e:
        log.export(f"Bras data upload failed. {e}", err=True)
    finally:
        log.export("Updater bras data finished", info=True)
    try:
        log.export("Starting updater caching data...", warn=True)
        cachingHandler = CachingUpdaterHandler()
        if date:
            data_borde = cachingHandler.get_data(date=date)
        else:
            data_borde = cachingHandler.get_data()
        cachingHandler.load_data(data=data_borde)
    except Exception as e:
        log.export(f"Caching data upload failed. {e}", err=True)
    finally:
        log.export("Updater caching data finished", info=True)
    try:
        log.export("Starting updater rai data...", warn=True)
        raiHandler = RaiUpdaterHandler()
        if date:
            data_borde = raiHandler.get_data(date=date)
        else:
            data_borde = raiHandler.get_data()
        raiHandler.load_data(data=data_borde)
    except Exception as e:
        log.export(f"Rai data upload failed. {e}", err=True)
    finally:
        log.export("Updater rai data finished", info=True)


if __name__ == "__main__":
    cli()
