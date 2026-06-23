from pydantic import BaseModel


class SourceModel(BaseModel):
    link: str
    enlace: str
    capacidad: int | float = 0
    model: str


class IpSourceModel(BaseModel):
    link: str
    enlace: str
