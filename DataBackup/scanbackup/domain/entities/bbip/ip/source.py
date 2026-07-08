from enum import Enum


class IPSourceBBIPField(str, Enum):
    LINK = "link"
    DEVICE = "device"
    STATUS = "status"
    LAYER = "layer"
