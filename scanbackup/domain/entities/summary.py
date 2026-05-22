from bson import ObjectId
from datetime import date
from pydantic import BaseModel


class BBIPDailySummaryEntity(BaseModel):
    """Data structure of the daily report."""

    date: date
    in_prom: float
    in_max: float
    out_prom: float
    out_max: float
    use: float
    id_source: ObjectId


class IPDailySummaryEntity(BaseModel):
    """Data structure of the daily report."""

    date: date
    in_prom: float
    in_max: float
    id_source: ObjectId
