from pydantic import BaseModel


class DailyReportModel(BaseModel):
    """Daily report data model."""

    name: str
    type: str
    capacity: int
    date: str
    typeLayer: str
    inProm: int
    outProm: int
    inMax: int
    outMax: int
    use: float