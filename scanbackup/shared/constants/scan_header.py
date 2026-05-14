from enum import Enum


class SCANHeader(Enum):
    DATE = "Date"
    TIME = "Time"
    IN_PROM = "In Prom"
    OUT_PROM = "Out Prom"
    IN_MAX = "In Max"
    OUT_MAX = "Out Max"
