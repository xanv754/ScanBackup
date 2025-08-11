import click
from multiprocessing import Process
from systemgrd.updater.handler.borde import BordeUpdaterHandler, BordeSourceScrapping
from systemgrd.updater.handler.bras import BrasUpdaterHandler, BrasSourceScrapping
from systemgrd.updater.handler.caching import CachingUpdaterHandler, CachingSourceScrapping
from systemgrd.updater.handler.rai import RaiUpdaterHandler, RaiSourceScrapping
from systemgrd.updater.handler.dailyReport import DailyReportUpdaterHandler
from systemgrd.utils import log


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
def data(date: str, force: bool = False):
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

@cli.command(help="Recarga los enlaces para obtener la información de SCAN.")
@click.option("--borde", required=False, is_flag=True, help="Actualizar solo los enlaces de SCAN para la capa Borde.")
@click.option("--bras", required=False, is_flag=True, help="Actualizar solo los enlaces de SCAN para la capa Bras.")
@click.option("--caching", required=False, is_flag=True, help="Actualizar solo los enlaces de SCAN para la capa Caching.")
@click.option("--rai", required=False, is_flag=True, help="Actualizar solo los enlaces de SCAN para la capa Rai.")
def sources(borde: bool = False, bras: bool = False, caching: bool = False, rai: bool = False):
    log.info("Starting scrapping to update sources...")
    if (not borde and not bras and not caching and not rai) or borde:
        log.info("Starting update of sources for Borde layer...")
        borde_scrapper = BordeSourceScrapping()
        borde_sources = borde_scrapper.get_sources()
        log.info("Saving Borde sources...")
        status_update = borde_scrapper.save_sources(borde_sources, "Borde")
        if status_update: log.info("Sources from SCAN Borde updated.")
        else: log.error("Failed to update sources from SCAN Borde.")
    if (not borde and not bras and not caching and not rai) or bras:
        log.info("Starting update of sources for Borde layer...")
        bras_scrapper = BrasSourceScrapping()
        bras_sources = bras_scrapper.get_sources()
        log.info("Saving Bras sources...")
        status_update = bras_scrapper.save_sources(bras_sources, "Bras")
        if status_update: log.info("Sources from SCAN Bras updated.")
        else: log.error("Failed to update sources from SCAN Bras.")
    if (not borde and not bras and not caching and not rai) or caching:
        log.info("Starting update of sources for Borde layer...")
        caching_scrapper = CachingSourceScrapping()
        caching_sources = caching_scrapper.get_sources()
        log.info("Saving Caching sources...")
        status_update = caching_scrapper.save_sources(caching_sources, "Caching")
        if status_update: log.info("Sources from SCAN Caching updated.")
        else: log.error("Failed to update sources from SCAN Caching.")
    if (not borde and not bras and not caching and not rai) or rai:
        log.info("Starting update of sources for Borde layer...")
        rai_scrapper = RaiSourceScrapping()
        rai_sources = rai_scrapper.get_sources()
        log.info("Saving Rai sources...")
        status_update = rai_scrapper.save_sources(rai_sources, "RAI")
        if status_update: log.info("Sources from SCAN Rai updated.")
        else: log.error("Failed to update sources from SCAN Rai.")


if __name__ == "__main__":
    cli()
