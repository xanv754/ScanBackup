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


@cli.command(help="Obtiene el reporte diario.")
@click.option("--date", required=False, help="Obtiene el resumen diario del día.")
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def diario(date: str | None = None, dev: bool = False):
    log.info("Obteniendo resumen diario...")
    status_operation = SummaryReportBBIP().summary_diary(date=date, dev=dev)
    if not status_operation:
        log.error("No se pudo generar el resumen diario")
    else:
        log.info("Resumen diario generado con éxito")


@cli.command(help="Obtiene el reporte semanal.")
@click.option(
    "--literal",
    is_flag=True,
    required=False,
    help="Obtiene el resumen semanal contando los 7 días hacia atrás.",
)
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def semanal(literal: bool = False, dev: bool = False):
    log.info("Obteniendo resumen semanal...")
    status_operation = SummaryReportBBIP().summary_weekly(literal=literal, dev=dev)
    if not status_operation:
        log.error("No se pudo generar el resumen semanal")
    else:
        log.info("Resumen semanal generado con éxito")


@cli.command(help="Obtiene el reporte quincenal.")
@click.option(
    "--literal",
    is_flag=True,
    required=False,
    help="Obtiene el resumen semanal contando los 15 días hacia atrás.",
)
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def quincenal(literal: bool = False, dev: bool = False):
    log.info("Obteniendo resumen quincenal...")
    status_operation = SummaryReportBBIP().summary_fortnight(literal=literal, dev=dev)
    if not status_operation:
        log.error("No se pudo generar el resumen quincenal")
    else:
        log.info("Resumen quincenal generado con éxito")


@cli.command(help="Obtiene el reporte mensual.")
@click.option(
    "--literal",
    is_flag=True,
    required=False,
    help="Obtiene el resumen semanal contando los 30 días hacia atrás.",
)
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def mensual(literal: bool = False, dev: bool = False):
    log.info("Obteniendo resumen mensual...")
    status_operation = SummaryReportBBIP().summary_monthly(literal=literal, dev=dev)
    if not status_operation:
        log.error("No se pudo generar el resumen mensual")
    else:
        log.info("Resumen mensual generado con éxito")


if __name__ == "__main__":
    cli()
