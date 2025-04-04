from enum import Enum


class BrasFieldDatabase(Enum):
    NAME = "name"
    TYPE = "btype"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class BordeFieldDatabase(Enum):
    INTERFACE = "interface"
    MODEL = "model"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class CachingFieldDatabase(Enum):
    INTERFACE = "interface"
    SERVICE = "service"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class RaiFieldDatabase(Enum):
    INTERFACE = "interface"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class TrafficHistoryFieldDatabase(Enum):
    DATE = "tdate"
    ID_LAYER = "idLayer"
    TYPE_LAYER = "typeLayer"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax" 


class IPHistoryFieldDatabase(Enum):
    DATE = "tdate"
    BRAS_NAME = "brasname"
    IN_PROM = "inProm"
    IN_MAX = "inMax"

