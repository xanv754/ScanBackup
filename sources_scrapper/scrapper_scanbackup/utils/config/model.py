from pydantic import BaseModel


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
    scan_credentials: CredentialModel
    layers: list[LayerModel]
