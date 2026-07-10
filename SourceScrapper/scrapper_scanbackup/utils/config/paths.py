import os
from pathlib import Path

ENV_BASE_DIR = "SCANBACKUP_HOME"


def get_base_dir() -> Path:
    """Directorio base para resolver `config.yml` y las rutas relativas del exporter.

    Se toma de la variable de entorno `SCANBACKUP_HOME` si está definida;
    en caso contrario, se usa el directorio de trabajo actual (`cwd`).
    """
    base_dir = os.environ.get(ENV_BASE_DIR)
    return Path(base_dir) if base_dir else Path.cwd()
