class BrasFieldDatabase:
    ID = "id"
    NAME = "name"
    TYPE = "type"
    CAPACITY = "capacity"
    SCAN = "scan"
    CREATE_AT = "createAt"
    UPDATE_AT = "updateAt"


class BordeFieldDatabase:
    ID = "id"
    NAME = "name"
    MODEL = "model"
    CAPACITY = "capacity"
    SCAN = "scan"
    CREATE_AT = "createAt"
    UPDATE_AT = "updateAt"


class CachingFieldDatabase:
    ID = "id"
    NAME = "name"
    SERVICE = "service"
    CAPACITY = "capacity"
    SCAN = "scan"
    CREATE_AT = "createAt"
    UPDATE_AT = "updateAt"


class RaiFieldDatabase:
    ID = "id"
    NAME = "name"
    CAPACITY = "capacity"
    SCAN = "scan"
    CREATE_AT = "createAt"
    UPDATE_AT = "updateAt"


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
    DATE = "date"
    TIME = "time"
    BRAS_NAME = "Bras"
    IN_PROM = "inProm"
    IN_MAX = "inMax"


class DailyReportFieldDatabase:
    DATE = "date"
    ID_LAYER = "idLayer"
    TYPE_LAYER = "typeLayer"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax"