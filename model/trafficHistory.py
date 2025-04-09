from pydantic import BaseModel


class TrafficHistoryModel(BaseModel):
    """Traffic model of layers history."""

    date: str
    time: str
    idLayer: str
    typeLayer: str
    inProm: int
    inMax: int
    outProm: int
    outMax: int
