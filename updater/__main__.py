import click
from multiprocessing import Process
from constants.group import LayerType
from updater import (
    BordeUpdaterHandler,
    BrasUpdaterHandler,
    CachingUpdaterHandler,
    RaiUpdaterHandler, 
    DailyReportUpdaterHandler
)
from utils.log import log


def load_borde(date: str | None) -> None:
    try:
        borderHandler = BordeUpdaterHandler()
        if date: data_borde = borderHandler.get_data(date=date)
        else: data_borde = borderHandler.get_data()
        borderHandler.load_data(data=data_borde)
    except Exception as e:
        log.error(f"Failed to load data of Border layer. {e}")

def load_bras(date: str | None) -> None:
    try:
        brasHandler = BrasUpdaterHandler()
        if date: data_bras = brasHandler.get_data(date=date)
        else: data_bras = brasHandler.get_data()
        brasHandler.load_data(data=data_bras)
    except Exception as e:
        log.error(f"Failed to load data of Bras layer. {e}")

def load_caching(date: str | None) -> None:
    try:
        cachingHandler = CachingUpdaterHandler()
        if date: data_caching = cachingHandler.get_data(date=date)
        else: data_caching = cachingHandler.get_data()
        cachingHandler.load_data(data=data_caching)
    except Exception as e:
        log.error(f"Failed to load data of Caching layer. {e}")

def load_rai(date: str | None) -> None:
    try:
        raiHandler = RaiUpdaterHandler()
        if date: data_rai = raiHandler.get_data(date=date)
        else: data_rai = raiHandler.get_data()
        raiHandler.load_data(data=data_rai)
    except Exception as e:
        log.error(f"Failed to load data of Rai layer. {e}")

def load_daily_report(layer_type: str, date: str | None) -> None:
    try:
        dailyReportHandler = DailyReportUpdaterHandler()
        if date:
            dailyReportHandler.generate_report(layer_type=layer_type, date=date)
        else:
            dailyReportHandler.generate_report(layer_type=layer_type)
    except Exception as e:
        log.error(f"Failed to load data of Daily report layer. {e}")


@click.group
def cli():
    """CLI Updater Database"""
    pass


@cli.command(help="Upload data obtained to database")
@click.option("--date", required=False, help="Date to upload data. Format YYYY-MM-DD")
def data(date: str):
    try:
        log.info("Starting updater data...")
        if not date: date = None
        borde = Process(target=load_borde, args=(date,))
        borde.start()
        bras = Process(target=load_bras, args=(date,))
        bras.start()
        caching = Process(target=load_caching, args=(date,))
        caching.start()
        rai = Process(target=load_rai, args=(date,))
        rai.start()
        borde.join()
        bras.join()
        caching.join()
        rai.join()
    except Exception as e:
        log.error(f"Data upload failed. {e}")
    finally:
        log.info("Updater data finished")
    # try:
    #     log.info("Generating daily reports...")
    #     borde = Process(target=load_daily_report, args=(LayerType.BORDE, date))
    #     borde.start()
    #     bras = Process(target=load_daily_report, args=(LayerType.BRAS, date))
    #     bras.start()
    #     caching = Process(target=load_daily_report, args=(LayerType.CACHING, date))
    #     caching.start()
    #     rai = Process(target=load_daily_report, args=(LayerType.RAI, date))
    #     rai.start()
    #     borde.join()
    #     bras.join()
    #     caching.join()
    #     rai.join()
    # except Exception as e:
    #     log.error(f"Daily report generation failed. {e}")
    # finally:
    #     log.info("Generating daily reports finished")


if __name__ == "__main__":
    cli()
