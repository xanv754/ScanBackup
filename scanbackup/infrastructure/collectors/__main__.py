import click
import subprocess
from datetime import datetime
from scanbackup.shared import (
    PathConfig,
    SCAN_COLLECTOR_SEPARATOR_FILE,
    SCAN_COLLECTOR_FORMAT_DATE,
    ScanCredentialEnvironment,
)


@click.group()
def cli_collector() -> None:
    pass


@cli_collector.command(help="Executa la captura de tráfico de SCAN")
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
@click.option(
    "--dev", is_flag=True, required=False, help="Carga el entorno de desarrollo."
)
def run(date: str | None = None, layer: str | None = None, dev: bool = False) -> None:
    layers: list[str] = []
    config = ScanCredentialEnvironment(dev=dev)
    credentials = config.get_credentials()
    PathConfig.create_folder(
        PathConfig.FOLDER_SOURCES
    )  # TODO: Refactorizar para que si no hay fuentes no haga nada
    PathConfig.create_folder(PathConfig.FOLDER_BBIP_DATA)
    PathConfig.create_folder(PathConfig.FOLDER_TMP, empty=True)

    if not date:
        date = datetime.now().strftime(SCAN_COLLECTOR_FORMAT_DATE)
    if not layer:
        layers.append("BORDE")
        pass  # TODO: Recorrer todas las capas en paralelo
    else:
        layers.append(layer)

    for layer in layers:
        response = subprocess.run(
            [
                "bash",
                PathConfig.SCAN_SCRIPT,
                date,
                layer,
                SCAN_COLLECTOR_SEPARATOR_FILE,
                credentials.username.strip(),
                credentials.password.strip(),
                "Fecha;Hora;In Prom;Out Prom;In Max;Out Max",
                PathConfig.FOLDER_SOURCES.resolve(),
                PathConfig.FOLDER_BBIP_DATA.resolve(),
                PathConfig.FOLDER_TMP.resolve(),
                PathConfig.LOG_FILE.resolve(),
                "&",
                "_",
                "%Y-%m-%d",
            ],
            capture_output=True,
            text=True,
        )
        output = response.stdout
        print(output)
        error = response.stderr
        print(error)


if __name__ == "__main__":
    cli_collector()
