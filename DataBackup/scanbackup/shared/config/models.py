from pydantic import BaseModel, Field


class LayerModel(BaseModel):
    schema_collection: str
    names: list[str] = Field(default_factory=list)


class LogConfigModel(BaseModel):
    dir_name: str
    filename: str
    extension: str
    msg_format: str
    date_format: str


class ScanCredentialSchema(BaseModel):
    username: str
    password: str


class ScannerConfigModel(BaseModel):
    dir_storage: str
    dir_sources: str
    extension: str
    date_format: str
    file_delimiter: str
    port_separator_replacement: str
    space_separator_replacement: str
    scan_credentials: ScanCredentialSchema


class ReportConfigModel(BaseModel):
    preffix_name: str
    date_format: str


class LayerConfigModel(BaseModel):
    bbip: LayerModel
    ip: LayerModel


class DatabaseConfigModel(BaseModel):
    host: str
    port: int = Field(ge=1, le=65535)
    name: str
    user: str
    password: str


class MetadataConfigModel(BaseModel):
    dir_data: str
    logs: LogConfigModel
    scanner: ScannerConfigModel
    reports: ReportConfigModel


class ConfigModel(BaseModel):
    layers: LayerConfigModel
    database: DatabaseConfigModel
    metadata: MetadataConfigModel
