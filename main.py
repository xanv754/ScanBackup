import click
from controllers.summary import SummaryController
from utils.log import log

@click.group()
def cli():
    """CGPRD CLI.
    
    Un sistema para gestión y almacenamiento de los datos de los reportes de la 
    Coordinación Gestión Producto Red de Datos.
    """
    pass


@cli.command(help="Obtiene el reporte diario.")
@click.option("--date", required=False, help="Date to get data. Format YYYY-MM-DD")
def diario(date: str):
    log.info("Obteniendo resumen diario...")
    status_operation = SummaryController.summary_diary_current()
    if not status_operation: log.error("No se pudo obtener el resumen diario")
    else: log.info("Resumen diario obtenido")

@cli.command(help="Obtiene el reporte quincenal.")
def quincenal():
    SummaryController.summary_fortnight_current()

@cli.command(help="Obtiene el reporte semanal.")
def semanal():
    SummaryController.summary_weekly_current()

@cli.command(help="Obtiene el reporte mensual.")
def mensual():
    SummaryController.summary_monthly_current()


if __name__ == "__main__":
    cli()