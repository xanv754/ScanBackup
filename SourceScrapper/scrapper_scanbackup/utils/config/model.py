from pydantic import BaseModel, field_validator
from pathlib import Path


class ExporterModel(BaseModel):
    dir: Path
    delimiter: str

    @field_validator("dir")
    @classmethod
    def create_dir(cls, value: Path) -> Path:
        path = Path(__file__).parent.parent.parent.parent / value
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
