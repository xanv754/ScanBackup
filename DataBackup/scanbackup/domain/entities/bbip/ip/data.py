from enum import Enum
from pydantic import BaseModel
from datetime import date, time
from scanbackup.shared import PyObjectId


class IPActiveBBIPField(str, Enum):
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    DEVICE = "id_source"


class IPActiveBBIPEntity(BaseModel):
    date: date
    time: time
    in_prom: float
    in_max: float
    device: PyObjectId
