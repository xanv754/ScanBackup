class BrasFieldDatabase:
    NAME = "name"
    TYPE = "btype"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class BordeFieldDatabase:
    INTERFACE = "interface"
    MODEL = "model"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class CachingFieldDatabase:
    INTERFACE = "interface"
    SERVICE = "service"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class RaiFieldDatabase:
    INTERFACE = "interface"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class TrafficHistoryFieldDatabase:
    DATE = "date"
    TIME = "time"
    ID_LAYER = "idLayer"
    TYPE_LAYER = "typeLayer"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax"


class IPHistoryFieldDatabase:
    DATE = "tdate"
    BRAS_NAME = "brasname"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
