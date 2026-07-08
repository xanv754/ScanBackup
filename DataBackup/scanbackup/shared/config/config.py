from scanbackup.shared.config.models import (
    MetadataConfigModel,
    DatabaseConfigModel,
    LayerConfigModel,
    ConfigModel,
)
from pathlib import Path
import yaml


class Configuration:
    _instance: "Configuration | None" = None
    _filepath: Path = (
        Path(__file__).resolve().parent.parent.parent.parent / "config.yml"
    )
    _config: ConfigModel

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
        path = Path(__file__).parent.parent.parent.parent
        return str(path.resolve())

    def get_cfg(self) -> ConfigModel:
        return self._config

    def get_cfg_database(self) -> DatabaseConfigModel:
        return self._config.database

    def get_cfg_layers(self) -> LayerConfigModel:
        return self._config.layers

    def get_cfg_metadata(self) -> MetadataConfigModel:
        return self._config.metadata
