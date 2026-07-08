import click
from scanbackup.application.cli.history.updater import TrafficHistoryUpdater

@click.group()
def cli() -> None:
    """administrador del historial del sistema."""
    pass

@cli.command("upload", help="Almacena el tráfico obtenido de SCAN en el sistema")
@click.option("--layer", required=True, help="Capa a actualizar")
@click.option("--date", required=False, help="Fecha a cargar. Formato: YYYY-MM-DD")
def updater_traffic_history(layer: str, date: str | None = None) -> None:
    TrafficHistoryUpdater.execute(layer=layer, date_str=date)
