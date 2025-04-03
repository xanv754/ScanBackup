from enum import Enum


class BrasFieldDatabase(Enum):
    NAME = "name"
    TYPE = "btype"
    CAPACITY = "capacity"


class BordeFieldDatabase(Enum):
    INTERFACE = "interface"
    MODEL = "model"
    CAPACITY = "capacity"


class CachingFieldDatabase(Enum):
    INTERFACE = "interface"
    SERVICE = "service"
    CAPACITY = "capacity"


class RaiFieldDatabase(Enum):
    INTERFACE = "interface"
    CAPACITY = "capacity"


class IpBrasFieldDatabase(Enum):
    NAME = "name"
