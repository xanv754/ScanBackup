import click
from pathlib import Path
from scanbackup.application.cli.sources.extract_db import (
    traffic_export_from_database,
    ip_export_from_database,
)
from scanbackup.application.cli.sources.upload_db import (
    traffic_upload_to_database,
    ip_upload_to_database,
)
from scanbackup.application.cli.sources.updater import scrapper_sources


@click.group()
def cli() -> None:
    """administrador de fuentes del sistema."""
    pass


@cli.command(help="Actualiza fuentes de tráfico en el sistema")
@click.option(
    "--filepath",
    type=click.Path(exists=True, file_okay=True),
    required=True,
    help="Archivo de fuente para enlaces de tráfico BBIP",
)
def traffic_upload(filepath: str) -> None:
    traffic_upload_to_database(file=filepath)


@cli.command(help="Exporta las fuentes de tráfico del sistema")
@click.option(
    "--dirpath",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
    help="Ruta de la carpeta a exportar la data.",
)
@click.option(
    "--layer",
    type=str,
    required=False,
    help="Capa de la cual se quiere exportar la información",
)
def traffic_export(dirpath: str | None = None, layer: str | None = None) -> None:
    traffic_export_from_database(path=dirpath, layer=layer)


@cli.command(help="Actualiza fuentes de IP en el sistema")
@click.option(
    "--filepath",
    type=click.Path(exists=True, file_okay=True),
    required=True,
    help="Archivo de fuente para enlaces de IP BBIP",
)
def ip_upload(filepath: str) -> None:
    ip_upload_to_database(file=filepath)


@cli.command(help="Exporta las fuentes de IP del sistema")
@click.option(
    "--dirpath",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
    help="Ruta de la carpeta a exportar la data.",
)
@click.option(
    "--layer",
    type=str,
    required=False,
    help="Capa de la cual se quiere exportar la información",
)
def ip_export(dirpath: str | None = None, layer: str | None = None) -> None:
    ip_export_from_database(path=dirpath, layer=layer)


@cli.command(help="Obtiene un archivo con enlaces a consultar de SCAN")
@click.option(
    "--layer", default="all", help="Capa de la cual se quiere exportar la información"
)
@click.option(
    "--outdir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
    help="Ruta de la carpeta a exportar la data",
)
def updater(
    layer: str = "all",
    outdir: str | None = None,
) -> None:
    if outdir:
        scrapper_sources(layer=layer, outdir=Path(outdir))
    else:
        scrapper_sources(layer=layer)
