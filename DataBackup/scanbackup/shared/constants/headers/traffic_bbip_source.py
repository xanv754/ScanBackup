from enum import Enum


class TrafficSourceBBIPHeader(str, Enum):
    LINK = "link"
    INTERFACE = "enlace"
    TYPE = "model"
    CAPACITY = "capacidad"
