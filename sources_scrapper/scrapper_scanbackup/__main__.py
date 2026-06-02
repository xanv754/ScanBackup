import click
from scrapper_scanbackup.updater import UpdaterSources


@click.group()
def cli() -> None:
    """Módulo encargado de hacer un Scrapping a SCAN para obtener el archivo de fuentes"""
    pass


@cli.command(help="Exporta las fuentes de enlaces obtenidas de SCAN")
def run() -> None:
    updater = UpdaterSources()
    updater.main_borde()






if __name__ == "__main__":
    cli()
