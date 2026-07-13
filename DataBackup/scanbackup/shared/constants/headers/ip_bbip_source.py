from enum import Enum


class IPSourceBBIPHeader(str, Enum):
    LINK = "link"
    INTERFACE = "interface"
