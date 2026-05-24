import click
import time
from scanbackup.infrastructure.collectors.executer_scan import SCANScanner
from scanbackup.shared import Terminal, Log


@click.group()
def cli_collector() -> None:
    """Recolector de data de tráfico existente en SCAN"""
    pass


@cli_collector.command(help="Ejecuta la captura de tráfico de un día en SCAN")
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
def run(date: str | None = None, layer: str | None = None, dev: bool = False) -> None:
    terminal = Terminal()

    start_info = "Captura de tráfico existente en SCAN"
    Log.info(start_info)
    terminal.info(start_info)

    with terminal.status("Cargando configuración del sistema...") as status:
        try:
            scanner = SCANScanner()
            scanner.initialize(date=date)

            terminal.loading(status, "Iniciando captura de datos...")
            if not layer:
                scanner.execute_all()
            else:
                scanner.execute_layer(layer)
        except Exception:
            message = "Error en el proceso de captura de datos"
            Log.error("Error en el proceso de captura de datos")
            terminal.error(message)
            exit(1)
        else:
            message = "Proceso finalizado con éxito"
            Log.info(message)
            terminal.info(message)
