from enum import Enum


class IPActiveBBIPField(str, Enum):
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    DEVICE = "id_source"
