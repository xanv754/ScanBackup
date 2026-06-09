from enum import Enum


class IPDailySummaryBBIPField(str, Enum):
    DATE = "date"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    DEVICE = "id_source"
