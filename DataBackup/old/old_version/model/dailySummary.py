from pydantic import BaseModel


class DailySummaryModel(BaseModel):
    """Data model of the daily report."""

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
