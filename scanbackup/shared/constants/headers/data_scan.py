from enum import Enum


class SCANHeader(Enum):
    INTERFACE = "Interface"
    CAPACITY = "Capacity"
    MODEL = "Model"
    DATE = "Date"
    TIME = "Time"
    IN_PROM = "In_Prom"
    OUT_PROM = "Out_Prom"
    IN_MAX = "In_Max"
    OUT_MAX = "Out_Max"
    LAYER = "Layer"
