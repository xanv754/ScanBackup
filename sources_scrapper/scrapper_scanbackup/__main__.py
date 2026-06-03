import click
from scrapper_scanbackup.updater import UpdaterSources


@click.group()
def cli() -> None:
    """Módulo encargado de hacer un Scrapping a SCAN para obtener el archivo de fuentes"""
    pass


@cli.command(help="Exporta las fuentes de enlaces obtenidas de SCAN")
@click.option(
    "--layer",
    type=str,
    default="all",
    required=False,
    help="Capa de la cual se extraerán los enlaces",
)
def run(layer: str) -> None:
    updater = UpdaterSources()
    updater.execute(layer)


if __name__ == "__main__":
    cli()
