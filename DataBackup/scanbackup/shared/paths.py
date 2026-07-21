import os
from pathlib import Path

SCANBACKUP_HOME_ENV_VAR = "SCANBACKUP_HOME"
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent


def get_project_root() -> Path:
    """Return the project root directory used to locate config.yml and dir_data.

    Honors the SCANBACKUP_HOME environment variable when set. This is required
    because the package's installed location does not necessarily match the
    directory that holds config.yml and the data folder (e.g. a regular
    `pip install .` copies the package into site-packages). Without an
    override, it falls back to the repository root inferred from this file's
    location, which only holds when running from an editable/source checkout.
    """
    override = os.environ.get(SCANBACKUP_HOME_ENV_VAR)
    return Path(override).resolve() if override else _PACKAGE_ROOT
