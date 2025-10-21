from pydantic import BaseModel


class BBIPModel(BaseModel):
    """Data model of the Backbone IP."""

    name: str
    type: str
    capacity: int | float
    date: str
    time: str
    inValue: float
    inMax: float
    outValue: float
    outMax: float


class IPBrasModel:
    """Data model of the IP Bras."""

    brasname: str
    date: str
    time: str
    inProm: float
    inMax: float
