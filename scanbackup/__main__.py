import click
from scanbackup.infrastructure import database_cli
from scanbackup.application import updater_cli


@click.group()
def cli():
    """Scan Backup CLI.

    Un sistema para gestión y almacenamiento del tráfico de enlaces existentes en SCAN
    para uso de la Coordinación Gestión Producto Red de Datos.
    """
    pass


cli.add_command(database_cli, name="database")
cli.add_command(updater_cli, name="updater")

if __name__ == "__main__":
    cli()
