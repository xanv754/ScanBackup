from enum import Enum
from pydantic import BaseModel
from bson import ObjectId
from datetime import date, time


class TrafficBBIPField(str, Enum):
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    OUT_PROM = "outProm"
    OUT_MAX = "outMax"
    DEVICE = "id_source"


class TrafficBBIPEntity(BaseModel):
    date: date
    time: time
    in_prom: float
    in_max: float
    out_prom: float
    out_max: float
    device: ObjectId
