import yaml
from scrapper_scanbackup.utils.config.model import (
    ConfigModel,
    CredentialModel,
    LayerModel,
    ExporterModel,
    HeaderModel,
)
from scrapper_scanbackup.utils.config.paths import get_base_dir


class ScrapperSetting:
    _config: ConfigModel

    def __init__(self) -> None:
        self._load_config()

    def _load_config(self) -> None:
        """Carga y valida `config.yml` desde el directorio base (ver `get_base_dir`)."""
        filepath = get_base_dir() / "config.yml"
        if not filepath.exists():
            raise FileNotFoundError("No se encuentra el archivo de configuración")
        raw = yaml.safe_load(filepath.read_text())
        self._config = ConfigModel.model_validate(raw)

    def get_header(self) -> HeaderModel:
        return self._config.header

    def get_exporter(self) -> ExporterModel:
        return self._config.exporter

    def get_scan_credentials(self) -> CredentialModel:
        return self._config.scan_credentials

    def get_data_layer(self, search_layer: str) -> list[LayerModel]:
        data = []
        for layer in self._config.layers:
            if layer.layer == search_layer:
                data.append(layer)
        return data
