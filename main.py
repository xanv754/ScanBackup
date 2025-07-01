import click
from reports.summary import SummaryController
from utils.log import log

@click.group()
def cli():
    """CGPRD CLI.
    
    Un sistema para gestión y almacenamiento de los datos de los reportes de la 
    Coordinación Gestión Producto Red de Datos.
    """
    pass


@cli.command(help="Obtiene el reporte diario.")
def diario(date: str):
    log.info("Obteniendo resumen diario...")
    status_operation = SummaryController.summary_diary_current()
    if not status_operation: log.error("No se pudo obtener el resumen diario")
    else: log.info("Resumen diario obtenido")

@cli.command(help="Obtiene el reporte semanal.")
def semanal():
    log.info("Obteniendo resumen semanal...")
    status_operation =SummaryController.summary_weekly_current()
    if not status_operation: log.error("No se pudo obtener el resumen semanal")
    else: log.info("Resumen semanal obtenido")

@cli.command(help="Obtiene el reporte quincenal.")
def quincenal():
    log.info("Obteniendo resumen quincenal...")
    status_operation = SummaryController.summary_fortnight_current()
    if not status_operation: log.error("No se pudo obtener el resumen quincenal")
    else: log.info("Resumen quincenal obtenido")

@cli.command(help="Obtiene el reporte mensual.")
def mensual():
    log.info("Obteniendo resumen mensual...")
    status_operation =SummaryController.summary_monthly_current()
    if not status_operation: log.error("No se pudo obtener el resumen mensual")
    else: log.info("Resumen mensual obtenido")


if __name__ == "__main__":
    cli()