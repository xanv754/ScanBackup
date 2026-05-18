import click
import time
from scanbackup.infrastructure.collectors.executer_scan import SCANScanner
from scanbackup.shared import Terminal


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
    help="Captura el tráfico de UNA capa de SCAN en específico. Debe escribirse todo en mayúscula.",
)
@click.option(
    "--dev", is_flag=True, required=False, help="Carga configuración de desarrollo."
)
def run(date: str | None = None, layer: str | None = None, dev: bool = False) -> None:
    terminal = Terminal()
    terminal.info("Iniciando captura de tráfico de SCAN...")
    with terminal.status("Obteniendo información de las capas BBIP...") as status:
        scanner = SCANScanner()
        scanner.initialize(date=date, dev=dev)
        if not layer:
            scanner.execute_all()
        else:
            scanner.execute_layer(layer)

        time.sleep(10)

    terminal.info("Captura de tráfico de SCAN finalizada.")
