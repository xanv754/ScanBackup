import click
from scanbackup.application.cli.reports.generator import (
    TrafficDailyReportGenerator,
    TrafficMonthlyReportGenerator,
    TrafficWeeklyReportGenerator,
    TrafficBiweeklyReportGenerator,
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
    "--literal",
    is_flag=True,
    default=False,
    help="Cuenta el mes como los 30 días previos a hoy, en vez del rango 01-último día del mes.",
)
@click.option(
    "--dirpath",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
    help="Ruta de la carpeta donde exportar el reporte.",
)
def generate_monthly_traffic_report(
    month: str | None = None, literal: bool = False, dirpath: str | None = None
) -> None:
    filepath = TrafficMonthlyReportGenerator.execute(
        month_str=month, literal=literal, output_dir=dirpath
    )
    click.echo(f"Reporte generado: {filepath}")


@cli.command(
    "weekly-traffic",
    help="Genera el reporte semanal (del lunes anterior al domingo de la semana cursando) de tráfico de todas las interfaces activas, agrupadas por capa, en un archivo .xlsx",
)
@click.option(
    "--literal",
    is_flag=True,
    default=False,
    help="Cuenta la semana como los 7 días previos a hoy, en vez del rango domingo-primero por defecto.",
)
@click.option(
    "--dirpath",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
    help="Ruta de la carpeta donde exportar el reporte.",
)
def generate_weekly_traffic_report(
    literal: bool = False, dirpath: str | None = None
) -> None:
    filepath = TrafficWeeklyReportGenerator.execute(literal=literal, output_dir=dirpath)
    click.echo(f"Reporte generado: {filepath}")


@cli.command(
    "biweekly-traffic",
    help="Genera el reporte quincenal de tráfico de todas las interfaces activas, agrupadas por capa, en un archivo .xlsx",
)
@click.option(
    "--month", required=False, help="Mes a reportar (del 01 al 15). Formato: YYYY-MM"
)
@click.option(
    "--literal",
    is_flag=True,
    default=False,
    help="Cuenta la quincena como los 15 días previos a hoy, en vez del rango 01-15 del mes.",
)
@click.option(
    "--dirpath",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
    help="Ruta de la carpeta donde exportar el reporte.",
)
def generate_biweekly_traffic_report(
    month: str | None = None, literal: bool = False, dirpath: str | None = None
) -> None:
    filepath = TrafficBiweeklyReportGenerator.execute(
        month_str=month, literal=literal, output_dir=dirpath
    )
    click.echo(f"Reporte generado: {filepath}")
