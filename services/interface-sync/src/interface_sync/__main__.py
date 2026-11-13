import sys
from collections.abc import Callable

import click

from interface_sync.constants.enums import LogEvent
from interface_sync.exceptions import MissingCredentialsError, MissingDatabaseSettingsError
from interface_sync.models import ExitCode
from interface_sync.orchestration import SyncOrchestratorBuilder


def _execute(command: Callable[[SyncOrchestratorBuilder], ExitCode]) -> None:
    """Run a command with a fresh builder, report unexpected errors and exit with its code."""
    builder = SyncOrchestratorBuilder()
    try:
        exit_code = command(builder)
    except (MissingCredentialsError, MissingDatabaseSettingsError) as error:
        builder.logger.error(LogEvent.PROCESS_ERROR, str(error))
        builder.terminal.error(str(error))
        exit_code = ExitCode.PROCESS_ERROR
    except Exception as error:
        builder.logger.error(LogEvent.PROCESS_ERROR, f"error inesperado: {error!r}")
        builder.terminal.error(f"Error inesperado: {error!r}")
        exit_code = ExitCode.PROCESS_ERROR
    finally:
        builder.close()
    sys.exit(exit_code)


@click.group(help="Sincroniza las interfaces de red de SCAN con la base de datos.")
def cli() -> None:
    """Group of commands of the service."""


@cli.command(name="run")
def run() -> None:
    """Obtiene las interfaces de SCAN y sincroniza la base de datos.

    Lee las páginas declaradas en config.yml (ruta en CONFIG_PATH), verifica SCAN y la
    base de datos, y procesa cada página. Las credenciales de SCAN se toman de las
    variables de entorno SCAN_USERNAME y SCAN_PASSWORD.

    \b
    Códigos de salida:
      0  todas las páginas se procesaron con éxito
      1  al menos una página falló
      2  error general del proceso (configuración inválida, credenciales ausentes,
         SCAN o base de datos no disponibles, error inesperado)
    """
    _execute(lambda builder: builder.build().run())


@cli.command(name="check-scan")
def check_scan() -> None:
    """Verifica solamente que SCAN responda.

    Lee las páginas declaradas en config.yml (ruta en CONFIG_PATH) y consulta cada ruta base
    (esquema y host) con las credenciales SCAN_USERNAME y SCAN_PASSWORD. No usa la base de
    datos ni procesa páginas. El resultado se muestra por terminal y se registra en el log.

    \b
    Códigos de salida:
      0  todas las rutas base responden
      2  configuración inválida, credenciales ausentes o alguna ruta sin respuesta
    """
    _execute(lambda builder: builder.build_scan_check().run())


if __name__ == "__main__":
    cli()
