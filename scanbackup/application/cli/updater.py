import click
from pathlib import Path
from scanbackup.infrastructure import MongoTrafficBBIPRepository
from scanbackup.application.use_case.bbip.updaters.source_traffic import (
    UpdateBBIPSources,
)
from scanbackup.shared import Terminal, Log


@click.group()
def cli() -> None:
    """Actualizador de datos del sistema"""


@cli.command(help="Actualizar fuentes para el scanner")
@click.option(
    "--filepath",
    type=click.Path(exists=True, file_okay=True),
    required=True,
    help="Archivo de fuente para enlaces de tráfico BBIP",
)
def bbip_traffic_src(filepath: str) -> None:
    terminal = Terminal()

    message = "Actualizando de información de archivos fuentes de tráfico para el BBIP"
    Log.info(message)
    terminal.info(message)

    with terminal.status("Configurando sistema...") as status:
        try:
            filepath = Path(filepath)
            repository = MongoTrafficBBIPRepository()

            terminal.loading(status, "Procesando información")

            process = UpdateBBIPSources(repository=repository, filepath=filepath)
            process.execute()
        except Exception:
            terminal.error("Falla de actualización de los archivos fuentes")
        else:
            terminal.info("Proceso finalizado con éxito")


if __name__ == "__main__":
    cli()
