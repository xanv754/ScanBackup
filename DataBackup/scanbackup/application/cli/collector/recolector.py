from scanbackup.infrastructure.collectors import SCANScanner
from scanbackup.shared import Terminal, Log


def recolector(date: str | None = None, layer: str | None = None) -> None:
    terminal = Terminal()

    start_info = "Captura de tráfico existente en SCAN"
    Log.info(start_info)
    terminal.info(start_info)

    with terminal.status("Cargando configuración del sistema...") as status:
        try:
            scanner = SCANScanner()
            scanner.initialize(date=date)

            terminal.loading(status, "Iniciando captura de datos...")
            if not layer:
                scanner.execute_all()
            else:
                scanner.execute_layer(layer)
        except Exception:
            message = "Error en el proceso de captura de datos"
            Log.error("Error en el proceso de captura de datos")
            terminal.error(message)
            exit(1)
        else:
            message = "Proceso finalizado con éxito"
            Log.info(message)
            terminal.info(message)
