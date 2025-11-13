from pydantic import BaseModel


class BBIPModel(BaseModel):
    """Data model of the Backbone IP."""

    name: str
    type: str
    capacity: int | float
    date: str
    time: str
    inProm: float
    inMaxProm: float
    outProm: float
    outMaxProm: float


class IPBrasModel(BaseModel):
    """Data model of the IP Bras."""

    brasname: str
    date: str
    time: str
    inProm: float
    inMax: float | None = None  # Hacer opcional para manejar NaN
