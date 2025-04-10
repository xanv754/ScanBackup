from pydantic import BaseModel


class BorderModel(BaseModel):
    """Border data model."""

    interface: str
    model: str
    capacity: int

class BordeTrafficModel(BaseModel):
    """Borde with data history traffic model."""
    interface: str
    model: str
    capacity: int
    date: str
    time: str
    inProm: int
    inMax: int
    outProm: int
    outMax: int