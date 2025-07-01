from pydantic import BaseModel


class DailyReportModel(BaseModel):
    """Data model of the daily report."""

    name: str
    type: str
    capacity: int | float
    date: str
    typeLayer: str
    inProm: float
    inMaxProm: float
    outProm: float
    outMaxProm: float
    use: float