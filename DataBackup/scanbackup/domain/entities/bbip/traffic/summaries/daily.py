from enum import Enum
from datetime import date
from pydantic import BaseModel
from scanbackup.shared import PyObjectId


class TrafficDailySummaryBBIPField(str, Enum):
    DATE = "date"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax"
    USE = "use"
    DEVICE = "id_source"


class TrafficDailySummaryBBIPEntity(BaseModel):
    date: date
    in_prom: float
    in_max: float
    out_prom: float
    out_max: float
    use: float
    device: PyObjectId
