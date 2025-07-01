import click
from reports import SummaryReportBBIP
from utils.log import log

@click.group()
def cli():
    """CGPRD CLI.
    
    Un sistema para gestión y almacenamiento de los datos de los reportes de la 
    Coordinación Gestión Producto Red de Datos.
    """
    pass


@cli.command(help="Obtiene el reporte diario.")
@click.option("--date", required=False, help="Obtiene el resumen diario del día.")
def diario(date: str):
    log.info("Obteniendo resumen diario...")
    if date: status_operation = SummaryReportBBIP().summary_diary(date=date)
    else: status_operation = SummaryReportBBIP().summary_diary()
    if not status_operation: log.error("No se pudo obtener el resumen diario")
    else: log.info("Resumen diario obtenido")

@cli.command(help="Obtiene el reporte semanal.")
@click.option("--literal", required=False, help="Obtiene el resumen semanal contando los 7 días hacia atrás.")
def semanal():
    log.info("Obteniendo resumen semanal...")
    status_operation =SummaryReportBBIP().summary_weekly()
    if not status_operation: log.error("No se pudo obtener el resumen semanal")
    else: log.info("Resumen semanal obtenido")

@cli.command(help="Obtiene el reporte quincenal.")
def quincenal():
    log.info("Obteniendo resumen quincenal...")
    status_operation = SummaryReportBBIP().summary_fortnight()
    if not status_operation: log.error("No se pudo obtener el resumen quincenal")
    else: log.info("Resumen quincenal obtenido")

@cli.command(help="Obtiene el reporte mensual.")
def mensual():
    log.info("Obteniendo resumen mensual...")
    status_operation =SummaryReportBBIP().summary_monthly()
    if not status_operation: log.error("No se pudo obtener el resumen mensual")
    else: log.info("Resumen mensual obtenido")


if __name__ == "__main__":
    cli()