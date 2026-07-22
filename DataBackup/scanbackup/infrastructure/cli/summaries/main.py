import click
from scanbackup.infrastructure.cli.summaries.updater import (
    TrafficSummaryUpdater,
    IPSummaryUpdater,
    TrafficHourSummaryUpdater,
    IPHourSummaryUpdater,
)

@click.group()
def cli() -> None:
    """administrador de los resúmenes del sistema."""
    pass

@cli.command(
    "traffic-generate",
    help="Genera el resumen diario de tráfico de todas las capas a partir del histórico almacenado",
)
@click.option("--date", required=False, help="Fecha a resumir. Formato: YYYY-MM-DD")
def generate_traffic_summary(date: str | None = None) -> None:
    TrafficSummaryUpdater.execute(date_str=date)

@cli.command(
    "ip-generate",
    help="Genera el resumen diario de IP activas de todas las capas a partir del histórico almacenado",
)
@click.option("--date", required=False, help="Fecha a resumir. Formato: YYYY-MM-DD")
def generate_ip_summary(date: str | None = None) -> None:
    IPSummaryUpdater.execute(date_str=date)

@cli.command(
    "traffic-generate-hour",
    help="Genera el resumen por hora de tráfico de todas las capas a partir del histórico almacenado",
)
@click.option("--date", required=False, help="Fecha a resumir. Formato: YYYY-MM-DD")
def generate_traffic_hour_summary(date: str | None = None) -> None:
    TrafficHourSummaryUpdater.execute(date_str=date)

@cli.command(
    "ip-generate-hour",
    help="Genera el resumen por hora de IP activas de todas las capas a partir del histórico almacenado",
)
@click.option("--date", required=False, help="Fecha a resumir. Formato: YYYY-MM-DD")
def generate_ip_hour_summary(date: str | None = None) -> None:
    IPHourSummaryUpdater.execute(date_str=date)
