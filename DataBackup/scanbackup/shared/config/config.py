from scanbackup.shared.config.models import (
    MetadataConfigModel,
    DatabaseConfigModel,
    LayerConfigModel,
    ConfigModel,
)
from scanbackup.shared.paths import get_project_root
from pathlib import Path
import os
import yaml


class Configuration:
    _instance: "Configuration | None" = None
    _filepath: Path = get_project_root() / "config.yml"
    _config: ConfigModel
    _database_env_vars: dict[str, str] = {
        "host": "SCANBACKUP_DB_HOST",
        "port": "SCANBACKUP_DB_PORT",
        "name": "SCANBACKUP_DB_NAME",
        "user": "SCANBACKUP_DB_USER",
        "password": "SCANBACKUP_DB_PASSWORD",
    }

    def __new__(cls) -> "Configuration":
        if not cls._instance:
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialize"):
            self._read_config()
            self._initialize = True

    def _read_config(self) -> None:
        raw = yaml.safe_load(self._filepath.read_text())
        self._config = ConfigModel.model_validate(raw)

    def get_filepath(self) -> str:
        return str(self._filepath.resolve())
    
    def get_projectpath(self) -> str:
        return str(get_project_root())

    def get_cfg(self) -> ConfigModel:
        return self._config

    def get_cfg_database(self) -> DatabaseConfigModel:
        """Return the database settings read from the SCANBACKUP_DB_* environment variables.

        The database is configured only in docker-compose.yml, which injects these
        variables into the container. For native runs they must be exported manually.
        Raises pydantic.ValidationError if any variable is missing or invalid.
        """
        raw = {
            field: os.environ.get(env_var)
            for field, env_var in self._database_env_vars.items()
            if os.environ.get(env_var) is not None
        }
        return DatabaseConfigModel.model_validate(raw)

    def get_cfg_layers(self) -> LayerConfigModel:
        return self._config.layers

    def get_cfg_metadata(self) -> MetadataConfigModel:
        return self._config.metadata
