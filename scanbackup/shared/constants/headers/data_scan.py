from enum import Enum


class SCANHeader(Enum):
    INTERFACE = "Interface"
    CAPACITY = "Capacity"
    MODEL = "Model"
    DATE = "Date"
    TIME = "Time"
    IN_PROM = "In Prom"
    OUT_PROM = "Out Prom"
    IN_MAX = "In Max"
    OUT_MAX = "Out Max"
    LAYER = "Layer"
