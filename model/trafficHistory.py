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


class TrafficHistoryFieldModel:
    """Traffic field model of layers history."""
    
    date: str = "date"
    time: str = "time"
    idLayer: str = "idLayer"
    typeLayer: str = "typeLayer"
    inProm: str = "inProm"
    inMax: str = "inMax"
    outProm: str = "outProm"
    outMax: str = "outMax"