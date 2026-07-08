import click
from scanbackup.application.cli.collector.recolector import recolector


@click.group()
def cli() -> None:
    """recolector de data de tráfico existente en SCAN"""
    pass


@cli.command(help="Ejecuta la captura de tráfico de un día en SCAN")
@click.option(
    "--date",
    required=False,
    help="Captura el tráfico de un día en específico. Formato: YYYY-MM-DD.",
)
@click.option(
    "--layer",
    required=False,
    help="Captura el tráfico de una capa de SCAN en específico. Debe escribirse todo en mayúscula.",
)
def run(date: str | None = None, layer: str | None = None) -> None:
    recolector(date=date, layer=layer)
