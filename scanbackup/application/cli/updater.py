import click
from pathlib import Path
from scanbackup.infrastructure import MongoTrafficSourceBBIPRepository
from scanbackup.application.use_case.bbip.updaters.source_traffic import (
    UpdateBBIPSources,
)
from scanbackup.shared import Configuration, Terminal, Log


@click.group()
def cli() -> None:
    """Actualizador de datos del sistema"""
    pass


@cli.group()
def bbip() -> None:
    """Administrador de información de BBIP"""
    pass


@bbip.group()
def sources() -> None:
    """Administrador de fuentes"""
    pass


@sources.command(help="Actualizar fuentes de tráfico")
@click.option(
    "--filepath",
    type=click.Path(exists=True, file_okay=True),
    required=True,
    help="Archivo de fuente para enlaces de tráfico BBIP",
)
def traffic_upload(filepath: str) -> None:
    terminal = Terminal()

    message = "Actualizando de información de archivos fuentes de tráfico para el BBIP"
    Log.info(message)
    terminal.info(message)

    with terminal.status("Configurando sistema...") as status:
        try:
            filepath = Path(filepath)
            repository = MongoTrafficSourceBBIPRepository()

            terminal.loading(status, "Procesando información...")

            process = UpdateBBIPSources(repository=repository, path=filepath)
            process.upload()
        except Exception:
            terminal.error("Falla de actualización de los archivos fuentes")
        else:
            terminal.info("Proceso finalizado con éxito")


@sources.command(help="Exporta las fuentes")
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
    terminal = Terminal()

    message = "Exportando información de fuentes de tráfico para el BBIP"
    Log.info(message)
    terminal.info(message)

    with terminal.status("Configurando sistema...") as status:
        try:
            system = Configuration()
            cfg_layers = system.get_cfg_layers()
            dirpath = Path(dirpath)
            repository = MongoTrafficSourceBBIPRepository()

            terminal.loading(status, "Exportando información...")

            process = UpdateBBIPSources(repository=repository, path=dirpath)
            if not layer:
                layers = cfg_layers.bbip.names
            else:
                layers = layers[layer]

            process.export(layers)
        except Exception:
            terminal.error("Falla de exportación de las fuentes")
        else:
            terminal.info("Proceso finalizado con éxito")


if __name__ == "__main__":
    cli()
