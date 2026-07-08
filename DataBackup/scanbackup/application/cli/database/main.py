import click
from scanbackup.application.cli.database.setup import setup_database
from scanbackup.application.cli.database.inspect import get_collection_names
from scanbackup.application.cli.database.import_data import import_data_to_database
from scanbackup.application.cli.database.export_data import (
    export_data_from_database,
)


@click.group()
def cli():
    """administrador de la base de datos"""
    pass


@cli.command(
    help="Crea todas las colecciones especificadas en la configuración del sistema."
)
def setup():
    setup_database()


@cli.command(
    help="Ver nombres de las colecciones actualmente existentes en la base de datos."
)
def inspect() -> None:
    get_collection_names()


@cli.command("import", help="Importa la data de un archivo .csv a una colección.")
@click.option(
    "--collection",
    required=True,
    help="Nombre de la colección de la base de datos a la que se quiere importar los datos.",
)
@click.option(
    "--filepath",
    type=click.Path(exists=True),
    required=True,
    help="Ruta del archivo .csv a importar.",
)
@click.option(
    "--delimiter",
    required=False,
    help="Delimitador de campos del archivo.",
)
def import_data(collection: str, filepath: str, delimiter: str = ";") -> None:
    import_data_to_database(
        collection=collection, filepath=filepath, delimiter=delimiter
    )


@cli.command("export", help="Exporta la data de colección en un archivo .csv.")
@click.option(
    "--collection",
    required=True,
    help="Nombre de la colección de la base de datos a la que se quiere exportar los datos.",
)
@click.option(
    "--dirpath",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Ruta de la carpeta a exportar la data.",
)
@click.option("--delimiter", required=False, help="Delimitador de campos del archivo.")
@click.option("--id", is_flag=True, required=False, help="Incluir el ID en el archivo.")
def export_data(
    collection: str,
    dirpath: str,
    delimiter: str | None = None,
    id: bool = False,
) -> None:
    export_data_from_database(
        collection=collection, dirpath=dirpath, delimiter=delimiter, id=id
    )
