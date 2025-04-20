from pydantic import BaseModel


class BordeModel(BaseModel):
    """Borde data model."""

    id: str | None
    name: str
    model: str
    capacity: int
    createAt: str

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
