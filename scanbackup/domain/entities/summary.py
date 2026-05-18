from pydantic import BaseModel


class DailySummaryEntity(BaseModel):
    """Data structure of the daily report."""

    name: str
    type: str
    capacity: int | float
    date: str
    typeLayer: str
    inProm: float
    outProm: float
    inMaxProm: float
    outMaxProm: float
    use: float
