from enum import Enum


class TrafficSourceBBIPHeader(str, Enum):
    LINK = "link"
    INTERFACE = "enlace"
    TYPE = "tipo"
    CAPACITY = "capacidad"
