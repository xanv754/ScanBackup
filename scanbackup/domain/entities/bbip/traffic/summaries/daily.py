from enum import Enum


class TrafficDailySummaryBBIPField(str, Enum):
    DATE = "date"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax"
    USE = "use"
    DEVICE = "id_source"
