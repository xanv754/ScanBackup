import click
from scanbackup.application.cli.history.updater import (
    TrafficHistoryUpdater,
    IPHistoryUpdater,
)

@click.group()
def cli() -> None:
    """administrador del historial del sistema."""
    pass

@cli.command(
    "upload",
    help="Recolecta de SCAN el tráfico de las fuentes activas de todas las capas y lo almacena en el sistema",
)
@click.option("--date", required=False, help="Fecha a recolectar. Formato: YYYY-MM-DD")
def updater_traffic_history(date: str | None = None) -> None:
    TrafficHistoryUpdater.execute(date_str=date)

@cli.command(
    "ip-upload",
    help="Recolecta de SCAN las IP activas de las fuentes activas de todas las capas y lo almacena en el sistema",
)
@click.option("--date", required=False, help="Fecha a recolectar. Formato: YYYY-MM-DD")
def updater_ip_history(date: str | None = None) -> None:
    IPHistoryUpdater.execute(date_str=date)
