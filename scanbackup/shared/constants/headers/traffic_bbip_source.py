from enum import Enum


class BBIPTrafficSourceHeader(str, Enum):
    LINK = "link"
    INTERFACE = "enlace"
    TYPE = "tipo"
    CAPACITY = "capacidad"
