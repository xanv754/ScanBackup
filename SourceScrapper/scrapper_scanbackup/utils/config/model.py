from pydantic import BaseModel, field_validator
from pathlib import Path
from scrapper_scanbackup.utils.config.paths import get_base_dir


class ExporterModel(BaseModel):
    dir: Path
    delimiter: str

    @field_validator("dir")
    @classmethod
    def create_dir(cls, value: Path) -> Path:
        """Resuelve `dir` contra el directorio base (ver `get_base_dir`) y lo crea si no existe."""
        path = get_base_dir() / value
        path.mkdir(parents=True, exist_ok=True)
        return path


class HeaderModel(BaseModel):
    link: str
    interface: str
    capacity: str
    type: str


class CredentialModel(BaseModel):
    username: str
    password: str


class LayerModel(BaseModel):
    layer: str
    url: str
    type: str
    locked: bool
    credentials: CredentialModel | None = None


class ConfigModel(BaseModel):
    exporter: ExporterModel
    header: HeaderModel
    scan_credentials: CredentialModel
    layers: list[LayerModel]
