import click
from multiprocessing import Process
from systemgrd.constants import LayerName
from systemgrd.updater.updater import UpdaterHandler, UpdaterSourceHandler
from systemgrd.utils import ConfigurationHandler, log


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
@click.option("--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo.")
def data(date: str | None = None, force: bool = False, dev: bool = False):
    try:
        log.info("Inicio de actualización de datos del sistema...")
        config = ConfigurationHandler(dev=dev)
        uri = config.uri_mongo
        borde = Process(target=UpdaterHandler, args=(LayerName.BORDE, uri, date, force))
        borde.start()
        bras = Process(target=UpdaterHandler, args=(LayerName.BRAS, uri, date, force))
        bras.start()
        caching = Process(target=UpdaterHandler, args=(LayerName.CACHING, uri, date, force))
        caching.start()
        rai = Process(target=UpdaterHandler, args=(LayerName.RAI, uri, date, force))
        rai.start()
        ixp = Process(target=UpdaterHandler, args=(LayerName.IXP, uri, date, force))
        ixp.start()
        borde.join()
        bras.join()
        caching.join()
        rai.join()
        ixp.join()
        log.info("Actualización de las capas finalizada")
        log.info("Inicio de actualización de reportes diarios del sistema...")
        status_operation = UpdaterHandler(
            layer=LayerName.DAILY_REPORT,
            uri=uri,
            date=date,
            force=force
        )
        if not status_operation: raise Exception()
        else: log.info("Actualización de reportes diarios cargado exitosamente")
        log.info("Actualización de reportes diarios finalizada")
    except Exception as e:
        log.error(f"Actualización de datos fallida. {e}")
    finally:
        log.info("Actualización del sistema finalizada")


@cli.command(help="Carga la data de los reportes diarios en el sistema.")
@click.option("--date", required=False, help="Fecha para cargar los datos. Formato YYYY-MM-DD")
@click.option("--force", is_flag=True, required=False, help="Carga todos los datos que puedan encontrarse obtenidos.")
@click.option("--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo.")
def daily(date: str | None = None, force: bool = False, dev: bool = False):
    try:
        log.info("Inicio de actualización de reportes diarios del sistema...")
        config = ConfigurationHandler(dev=dev)
        uri = config.uri_mongo
        status_operation = UpdaterHandler(
            layer=LayerName.DAILY_REPORT,
            uri=uri,
            date=date,
            force=force
        )
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
    log.info("Inicio de la actualización de las fuentes de SCAN...")
    if borde: UpdaterSourceHandler(LayerName.BORDE)
    if bras: UpdaterSourceHandler(LayerName.BRAS)
    if caching: UpdaterSourceHandler(LayerName.CACHING)
    if rai: UpdaterSourceHandler(LayerName.RAI)
    if not borde and not bras and not caching and not rai:
        UpdaterSourceHandler(LayerName.BORDE)
        UpdaterSourceHandler(LayerName.BRAS)
        UpdaterSourceHandler(LayerName.CACHING)
        UpdaterSourceHandler(LayerName.RAI)
    log.info("Actualización de las fuentes terminadas...")
    

if __name__ == "__main__":
    cli()
