from enum import Enum
from datetime import date
from pydantic import BaseModel


class TrafficDailyReportBBIPField(str, Enum):
    INTERFACE = "interface"
    MODEL = "model"
    CAPACITY = "capacity"
    LAYER = "layer"
    DATE = "date"
    IN_PROM = "in_prom"
    IN_MAX = "in_max"
    OUT_PROM = "out_prom"
    OUT_MAX = "out_max"
    USE = "use"


class TrafficDailyReportBBIPEntity(BaseModel):
    interface: str
    model: str
    capacity: float
    layer: str
    date: date
    in_prom: float
    in_max: float
    out_prom: float
    out_max: float
    use: float
