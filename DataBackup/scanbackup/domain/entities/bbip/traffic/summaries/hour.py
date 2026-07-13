from enum import Enum
from datetime import date, time
from pydantic import BaseModel
from scanbackup.shared import PyObjectId


class TrafficHourSummaryBBIPField(str, Enum):
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax"
    USE = "use"
    DEVICE = "id_source"


class TrafficHourSummaryBBIPEntity(BaseModel):
    date: date
    time: time
    in_prom: float
    in_max: float
    out_prom: float
    out_max: float
    use: float
    device: PyObjectId
