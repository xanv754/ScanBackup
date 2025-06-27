from pydantic import BaseModel


class BBIPModel(BaseModel):
    """Data model of the Backbone IP."""

    name: str
    type: str
    capacity: int | float
    date: str
    time: str
    inProm: float
    inMax: float
    outProm: float
    outMax: float


class IPBrasModel:
    """Data model of the IP Bras."""

    bras_name: str
    date: str
    time: str
    inProm: float
    inMax: float