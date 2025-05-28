from pydantic import BaseModel


class DailyReportModel(BaseModel):
    """Daily report data model."""

    date: str
    idLayer: str
    typeLayer: str
    inProm: float
    outProm: float
    inMax: float
    outMax: float


class DailyReportFieldModel:
    """Daily report field model."""
    
    date: str = "date"
    idLayer: str = "idLayer"
    typeLayer: str = "typeLayer"
    inProm: str = "inProm"
    outProm: str = "outProm"
    inMax: str = "inMax"
    outMax: str = "outMax"