import click
from systemgrd.reports import SummaryReportBBIP
from systemgrd.utils import log


@click.group()
def cli():
    """CGPRD CLI.

    Un sistema para gestión y almacenamiento de los datos de los reportes de la
    Coordinación Gestión Producto Red de Datos.
    """
    pass


@cli.command(help="Obtiene el reporte diario del BBIP.")
@click.option("--date", required=False, help="Obtiene el reporte diario del día del BBIP.")
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def diario(date: str | None = None, dev: bool = False):
    log.info("Obteniendo reporte diario del BBIP...")
    status_operation = SummaryReportBBIP().summary_diary(date=date, dev=dev)
    if not status_operation:
        log.error("No se pudo generar el reporte diario del BBIP")
    else:
        log.info("Reporte diario del BBIP generado con éxito")


@cli.command(help="Obtiene el reporte semanal del BBIP.")
@click.option(
    "--literal",
    is_flag=True,
    required=False,
    help="Obtiene el reporte semanal del BBIP contando los 7 días hacia atrás.",
)
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def semanal(literal: bool = False, dev: bool = False):
    log.info("Obteniendo reporte semanal del BBIP...")
    status_operation = SummaryReportBBIP().summary_weekly(literal=literal, dev=dev)
    if not status_operation:
        log.error("No se pudo generar el reporte semanal del BBIP")
    else:
        log.info("Reporte semanal del BBIP generado con éxito")


@cli.command(help="Obtiene el reporte quincenal del BBIP.")
@click.option(
    "--literal",
    is_flag=True,
    required=False,
    help="Obtiene el reporte quincenal del BBIP contando los 15 días hacia atrás.",
)
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def quincenal(literal: bool = False, dev: bool = False):
    log.info("Obteniendo reporte quincenal del BBIP...")
    status_operation = SummaryReportBBIP().summary_fortnight(literal=literal, dev=dev)
    if not status_operation:
        log.error("No se pudo generar el reporte quincenal del BBIP")
    else:
        log.info("Reporte quincenal del BBIP generado con éxito")


@cli.command(help="Obtiene el reporte mensual del BBIP.")
@click.option(
    "--literal",
    is_flag=True,
    required=False,
    help="Obtiene el reporte mensual del BBIP contando los 30 días hacia atrás.",
)
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def mensual(literal: bool = False, dev: bool = False):
    log.info("Obteniendo reporte mensual del BBIP...")
    status_operation = SummaryReportBBIP().summary_monthly(literal=literal, dev=dev)
    if not status_operation:
        log.error("No se pudo generar el reporte mensual del BBIP")
    else:
        log.info("Reporte mensual del BBIP generado con éxito")


if __name__ == "__main__":
    cli()
