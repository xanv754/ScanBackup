from pydantic import BaseModel


class BBIPEntity(BaseModel):
    """Data structure of the Backbone IP."""

    name: str
    type: str
    capacity: int | float
    date: str
    time: str
    inProm: float
    inMaxProm: float
    outProm: float
    outMaxProm: float


class IPBrasEntity(BaseModel):
    """Data model of the IP Bras."""

    brasname: str
    date: str
    time: str
    inProm: float
    inMaxProm: float
    capacity: float
    type: str
