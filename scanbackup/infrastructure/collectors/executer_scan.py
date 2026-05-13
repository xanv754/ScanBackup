import click
import subprocess
from scanbackup.shared import (
    PathConfig,
    SCAN_COLLECTOR_SEPARATOR_FILE,
    SCAN_COLLECTOR_FORMAT_DATE,
)


@click.group()
def cli_collector() -> None:
    pass


@click.command(help="Executa la captura de tráfico de SCAN")
@click.option(
    "--date",
    required=False,
    help="Captura el tráfico de un día en específico. Formato: YYYY-MM-DD.",
)
@click.option(
    "--layer",
    required=False,
    help="Captura el tráfico de UNA capa de SCAN en específico. Debe escribirse todo en mayúscula",
)
def run(date: str | None = None, layer: str | None = None) -> None:
    PathConfig.create_folder(PathConfig.FOLDER_TMP, empty=True)
    subprocess.run([f"bash "], capture_output=True, text=True)


if __name__ == "__main__":
    pass
