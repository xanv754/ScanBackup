import click
from multiprocessing import Process
from updater import (
    BordeUpdaterHandler,
    BrasUpdaterHandler,
    CachingUpdaterHandler,
    RaiUpdaterHandler, 
    DailyReportUpdaterHandler
)
from utils.log import log


def load_borde(date: str | None, force: bool = False) -> None:
    try:
        borderHandler = BordeUpdaterHandler()
        if date: data_borde = borderHandler.get_data(date=date, force=force)
        else: data_borde = borderHandler.get_data(force=force)
        status_operation = borderHandler.load_data(data=data_borde)
        if status_operation: log.info("Data de borde cargado exitosamente")
        else: log.error("Data de borde cargado fallida")
    except Exception as e:
        log.error(f"Failed to load data of Border layer. {e}")

def load_bras(date: str | None, force: bool = False) -> None:
    try:
        brasHandler = BrasUpdaterHandler()
        if date: data_bras = brasHandler.get_data(date=date, force=force)
        else: data_bras = brasHandler.get_data(force=force)
        status_operation = brasHandler.load_data(data=data_bras)
        if status_operation: log.info("Data de bras cargado exitosamente")        
        else: log.error("Data de bras cargado fallida")
    except Exception as e:
        log.error(f"Failed to load data of Bras layer. {e}")

def load_caching(date: str | None, force: bool = False) -> None:
    try:
        cachingHandler = CachingUpdaterHandler()
        if date: data_caching = cachingHandler.get_data(date=date, force=force)
        else: data_caching = cachingHandler.get_data(force=force)
        status_operation = cachingHandler.load_data(data=data_caching)
        if status_operation: log.info("Data de caching cargado exitosamente")
        else: log.error("Data de caching cargado fallida")
    except Exception as e:
        log.error(f"Failed to load data of Caching layer. {e}")

def load_rai(date: str | None, force: bool = False) -> None:
    try:
        raiHandler = RaiUpdaterHandler()
        if date: data_rai = raiHandler.get_data(date=date, force=force)
        else: data_rai = raiHandler.get_data(force=force)
        status_operation = raiHandler.load_data(data=data_rai)
        if status_operation: log.info("Data de rai cargado exitosamente")
        else: log.error("Data de rai cargado fallida")
    except Exception as e:
        log.error(f"Failed to load data of Rai layer. {e}")


@click.group
def cli():
    """SysGRD - Actualizador.

    Interfaz de línea de comandos para el manejo de operaciones para
    actualizar la data del sistema.
    """
    pass


@cli.command(help="Carga la data de SCAN en el sistema.")
@click.option("--date", required=False, help="Fecha para cargar los datos. Formato YYYY-MM-DD")
@click.option("--force", is_flag=True, required=False, help="Carga todos los datos que puedan encontrarse obtenidos.")
def data(date: str, force: bool):
    try:
        log.info("Inicio de actualización de datos del sistema...")
        if not date: date = None
        borde = Process(target=load_borde, args=(date, force))
        borde.start()
        bras = Process(target=load_bras, args=(date, force))
        bras.start()
        caching = Process(target=load_caching, args=(date, force))
        caching.start()
        rai = Process(target=load_rai, args=(date, force))
        rai.start()
        borde.join()
        bras.join()
        caching.join()
        rai.join()
    except Exception as e:
        log.error(f"Actualización de datos fallida. {e}")
    finally:
        log.info("Actualización del sistema finalizada")
    try:
        log.info("Inicio de actualización de reportes diarios del sistema...")
        dailyReportHandler = DailyReportUpdaterHandler()
        if date: reports = dailyReportHandler.get_data(date=date, force=force)
        else: reports = dailyReportHandler.get_data(force=force)
        status_operation = dailyReportHandler.load_data(data=reports)
        if not status_operation: raise Exception()
        else: log.info("Actualización de reportes diarios cargado exitosamente")
    except Exception as e:
        log.error(f"Actualización de reportes diarios fallida. {e}")
    finally:
        log.info("Actualización de reportes diarios finalizada")


@cli.command(help="Carga la data de los reportes diarios en el sistema.")
@click.option("--date", required=False, help="Fecha para cargar los datos. Formato YYYY-MM-DD")
@click.option("--force", is_flag=True, required=False, help="Carga todos los datos que puedan encontrarse obtenidos.")
def daily(date: str, force: bool = False):
    try:
        if not date: date = None
        log.info("Inicio de actualización de reportes diarios del sistema...")
        dailyReportHandler = DailyReportUpdaterHandler()
        if date: reports = dailyReportHandler.get_data(date=date, force=force)
        else: reports = dailyReportHandler.get_data(force=force)
        status_operation = dailyReportHandler.load_data(data=reports)
        if not status_operation: raise Exception()
        else: log.info("Actualización de reportes diarios cargado exitosamente")
    except Exception as e:
        log.error(f"Actualización de reportes diarios fallida. {e}")
    finally:
        log.info("Actualización de reportes diarios finalizada")


if __name__ == "__main__":
    cli()
