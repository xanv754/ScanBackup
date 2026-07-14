import click
from scanbackup.application.cli.reports.generator import (
    TrafficDailyReportGenerator,
    TrafficMonthlyReportGenerator,
)


@click.group()
def cli() -> None:
    """administrador de los reportes del sistema."""
    pass


@cli.command(
    "daily-traffic",
    help="Genera el reporte diario de tráfico de todas las interfaces activas, agrupadas por capa, en un archivo .xlsx",
)
@click.option("--date", required=False, help="Fecha a reportar. Formato: YYYY-MM-DD")
@click.option(
    "--dirpath",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
    help="Ruta de la carpeta donde exportar el reporte.",
)
def generate_daily_traffic_report(
    date: str | None = None, dirpath: str | None = None
) -> None:
    filepath = TrafficDailyReportGenerator.execute(date_str=date, output_dir=dirpath)
    click.echo(f"Reporte generado: {filepath}")


@cli.command(
    "monthly-traffic",
    help="Genera el reporte mensual de tráfico de todas las interfaces activas, agrupadas por capa, en un archivo .xlsx",
)
@click.option("--month", required=False, help="Mes a reportar. Formato: YYYY-MM")
@click.option(
    "--dirpath",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
    help="Ruta de la carpeta donde exportar el reporte.",
)
def generate_monthly_traffic_report(
    month: str | None = None, dirpath: str | None = None
) -> None:
    filepath = TrafficMonthlyReportGenerator.execute(month_str=month, output_dir=dirpath)
    click.echo(f"Reporte generado: {filepath}")
