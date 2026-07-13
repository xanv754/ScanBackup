from enum import Enum
from datetime import date
from pydantic import BaseModel
from scanbackup.shared import PyObjectId


class IPDailySummaryBBIPField(str, Enum):
    DATE = "date"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    DEVICE = "id_source"


class IPDailySummaryBBIPEntity(BaseModel):
    date: date
    in_prom: float
    in_max: float
    device: PyObjectId
