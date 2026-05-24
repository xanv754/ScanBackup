import click

from scanbackup.infrastructure.persistence.mongodb import cli_database


@click.group()
def cli():
    """Scan Backup CLI.

    Un sistema para gestión y almacenamiento del tráfico de enlaces existentes en SCAN
    para uso de la Coordinación Gestión Producto Red de Datos.
    """
    pass


cli.add_command(cli_database, name="database")

if __name__ == "__main__":
    cli()
