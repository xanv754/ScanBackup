from pydantic import BaseModel


class SourceModel(BaseModel):
    link: str
    enlace: str
    capacidad: int | float = 0
    tipo: str


class IpSourceModel(BaseModel):
    link: str
    enlace: str
