import click
from scanbackup.application.cli.database.main import cli as database_cli
from scanbackup.application.cli.history.main import cli as history_cli
from scanbackup.application.cli.summaries.main import cli as summaries_cli
from scanbackup.application.cli.reports.main import cli as reports_cli

@click.group()
def cli():
    """SCAN Backup CLI.

    Un sistema para gestión y almacenamiento del tráfico de enlaces existentes en SCAN
    para uso de la Coordinación Gestión Producto Red de Datos.
    """
    pass


cli.add_command(database_cli, name="database")
cli.add_command(history_cli, name="history")
cli.add_command(summaries_cli, name="summaries")
cli.add_command(reports_cli, name="reports")

try:
    # sources depende del paquete externo scrapper_scanbackup (proyecto
    # SourceScrapper), no declarado como dependencia de este proyecto. Se
    # registra solo si está disponible en el entorno.
    from scanbackup.application.cli.sources.main import cli as source_cli
except ModuleNotFoundError:
    pass
else:
    cli.add_command(source_cli, name="sources")

if __name__ == "__main__":
    cli()
