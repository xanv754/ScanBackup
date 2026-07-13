from enum import Enum
from datetime import date, time
from pydantic import BaseModel
from scanbackup.shared import PyObjectId


class IPHourSummaryBBIPField(str, Enum):
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    DEVICE = "id_source"


class IPHourSummaryBBIPEntity(BaseModel):
    date: date
    time: time
    in_prom: float
    in_max: float
    device: PyObjectId
