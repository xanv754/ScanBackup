import click
from scanbackup.application.cli.sources.extract_db import (
    traffic_export_from_database,
)
from scanbackup.application.cli.sources.upload_db import traffic_upload_to_database


@click.group()
def cli() -> None:
    """administrador de fuentes del sistema."""
    pass


@cli.command(help="Actualizar fuentes de tráfico")
@click.option(
    "--filepath",
    type=click.Path(exists=True, file_okay=True),
    required=True,
    help="Archivo de fuente para enlaces de tráfico BBIP",
)
def traffic_upload(filepath: str) -> None:
    traffic_upload_to_database(filepath=filepath)


@cli.command(help="Exporta las fuentes")
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
    traffic_export_from_database(dirpath=dirpath, layer=layer)
