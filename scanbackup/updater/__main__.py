import click
from multiprocessing import Process
from scanbackup.constants import LayerName
from scanbackup.updater.updater import UpdaterHandler, UpdaterSourceHandler
from scanbackup.utils import log, URIEnvironment


@click.group
def cli():
    """SysGRD - Actualizador.

    Interfaz de línea de comandos para el manejo de operaciones para
    actualizar la data del sistema.
    """
    pass


@cli.command(help="Carga la data de SCAN en el sistema.")
@click.option(
    "--date", required=False, help="Fecha para cargar los datos. Formato YYYY-MM-DD"
)
@click.option(
    "--borde",
    is_flag=True,
    required=False,
    help="Carga los datos de la capa Borde de SCAN.",
)
@click.option(
    "--bras",
    is_flag=True,
    required=False,
    help="Carga los datos de la capa Bras de SCAN.",
)
@click.option(
    "--caching",
    is_flag=True,
    required=False,
    help="Carga los datos de la capa Caching de SCAN.",
)
@click.option(
    "--rai",
    is_flag=True,
    required=False,
    help="Carga los datos de la capa Rai de SCAN.",
)
@click.option(
    "--ixp",
    is_flag=True,
    required=False,
    help="Carga los datos de la capa IXP de SCAN.",
)
@click.option(
    "--ipbras",
    is_flag=True,
    required=False,
    help="Carga los datos de la capa IPBras de SCAN.",
)
@click.option(
    "--force",
    is_flag=True,
    required=False,
    help="Carga todos los datos que puedan encontrarse obtenidos.",
)
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def data(
    date: str | None = None,
    borde: bool = False,
    bras: bool = False,
    caching: bool = False,
    rai: bool = False,
    ixp: bool = False,
    ipbras: bool = False,
    force: bool = False,
    dev: bool = False,
):
    try:
        log.info("Inicio de actualización de datos del sistema...")
        config = URIEnvironment(dev=dev)
        uri = config.get_uri_db()
        if borde and not bras and not caching and not rai and not ixp and not ipbras:
            borde_handler = Process(
                target=UpdaterHandler, args=(LayerName.BORDE, uri, date, force)
            )
            borde_handler.start()
            borde_handler.join()
            log.info("Actualización de la capa finalizada")
        elif bras and not borde and not caching and not rai and not ixp and not ipbras:
            bras_handler = Process(
                target=UpdaterHandler, args=(LayerName.BRAS, uri, date, force)
            )
            bras_handler.start()
            bras_handler.join()
            log.info("Actualización de la capa finalizada")
        elif caching and not borde and not bras and not rai and not ixp and not ipbras:
            caching_handler = Process(
                target=UpdaterHandler, args=(LayerName.CACHING, uri, date, force)
            )
            caching_handler.start()
            caching_handler.join()
            log.info("Actualización de la capa finalizada")
        elif rai and not borde and not bras and not caching and not ixp and not ipbras:
            rai_handler = Process(
                target=UpdaterHandler, args=(LayerName.RAI, uri, date, force)
            )
            rai_handler.start()
            rai_handler.join()
            log.info("Actualización de la capa finalizada")
        elif ixp and not borde and not bras and not caching and not rai and not ipbras:
            ixp_handler = Process(
                target=UpdaterHandler, args=(LayerName.IXP, uri, date, force)
            )
            ixp_handler.start()
            ixp_handler.join()
            log.info("Actualización de la capa finalizada")
        elif ipbras and not borde and not bras and not caching and not rai and not ixp:
            ipbras_handler = Process(
                target=UpdaterHandler, args=(LayerName.IP_BRAS, uri, date, force)
            )
            ipbras_handler.start()
            ipbras_handler.join()
            log.info("Actualización de la capa finalizada")
        else:
            borde_handler = Process(
                target=UpdaterHandler, args=(LayerName.BORDE, uri, date, force)
            )
            borde_handler.start()
            bras_handler = Process(
                target=UpdaterHandler, args=(LayerName.BRAS, uri, date, force)
            )
            bras_handler.start()
            caching_handler = Process(
                target=UpdaterHandler, args=(LayerName.CACHING, uri, date, force)
            )
            caching_handler.start()
            rai_handler = Process(
                target=UpdaterHandler, args=(LayerName.RAI, uri, date, force)
            )
            rai_handler.start()
            ixp_handler = Process(
                target=UpdaterHandler, args=(LayerName.IXP, uri, date, force)
            )
            ixp_handler.start()
            ipbras_handler = Process(
                target=UpdaterHandler, args=(LayerName.IP_BRAS, uri, date, force)
            )
            ipbras_handler.start()
            
            borde_handler.join()
            bras_handler.join()
            caching_handler.join()
            rai_handler.join()
            ixp_handler.join()
            ipbras_handler.join()
            log.info("Actualización de las capas finalizada")
        UpdaterHandler(
            layer=LayerName.DAILY_SUMMARY, uri=uri, date=date, force=force
        )
    except Exception as e:
        log.error(f"Actualización de datos fallida. {e}")
    finally:
        log.info("Actualización del sistema finalizada")


@cli.command(help="Carga la data de los reportes diarios en el sistema.")
@click.option(
    "--date", required=False, help="Fecha para cargar los datos. Formato YYYY-MM-DD"
)
@click.option(
    "--force",
    is_flag=True,
    required=False,
    help="Carga todos los datos que puedan encontrarse obtenidos.",
)
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def daily(date: str | None = None, force: bool = False, dev: bool = False):
    config = URIEnvironment(dev=dev)
    uri = config.get_uri_db()
    UpdaterHandler(
        layer=LayerName.DAILY_SUMMARY, uri=uri, date=date, force=force
    )


@cli.command(help="Recarga los enlaces para obtener la información de SCAN.")
@click.option(
    "--borde",
    required=False,
    is_flag=True,
    help="Actualizar solo los enlaces de SCAN para la capa Borde.",
)
@click.option(
    "--bras",
    required=False,
    is_flag=True,
    help="Actualizar solo los enlaces de SCAN para la capa Bras.",
)
@click.option(
    "--caching",
    required=False,
    is_flag=True,
    help="Actualizar solo los enlaces de SCAN para la capa Caching.",
)
@click.option(
    "--rai",
    required=False,
    is_flag=True,
    help="Actualizar solo los enlaces de SCAN para la capa Rai.",
)
@click.option(
    "--ipbras",
    required=False,
    is_flag=True,
    help="Actualizar solo los enlaces de SCAN para la capa IPBras.",
)
def sources(
    borde: bool = False,
    bras: bool = False,
    caching: bool = False,
    rai: bool = False,
    ipbras: bool = False,
):
    log.info("Inicio de la actualización de las fuentes...")
    if borde:
        UpdaterSourceHandler(LayerName.BORDE)
    if bras:
        UpdaterSourceHandler(LayerName.BRAS)
    if caching:
        UpdaterSourceHandler(LayerName.CACHING)
    if rai:
        UpdaterSourceHandler(LayerName.RAI)
    if ipbras:
        UpdaterSourceHandler(LayerName.IP_BRAS)
    if not borde and not bras and not caching and not rai and not ipbras:
        UpdaterSourceHandler(LayerName.BORDE)
        UpdaterSourceHandler(LayerName.BRAS)
        UpdaterSourceHandler(LayerName.CACHING)
        UpdaterSourceHandler(LayerName.RAI)
        UpdaterSourceHandler(LayerName.IP_BRAS)
    log.info("Actualización de las fuentes terminadas...")


if __name__ == "__main__":
    cli()
