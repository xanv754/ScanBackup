class TableName:
    BORDE = "BORDE_HISTORY"
    BRAS = "BRAS_HISTORY"
    CACHING = "CACHING_HISTORY"
    RAI = "RAI_HISTORY"
    IP_BRAS_HISTORY = "IP_BRAS_HISTORY"
    DAILY_REPORT = "DAILY_REPORT"


class BBIPFieldName:
    NAME = "name"
    TYPE = "type"
    CAPACITY = "capacity"
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    OUT_PROM = "outProm"
    OUT_MAX = "outMax"


class IPBrasHistoryFieldName:
    DATE = "date"
    TIME = "time"
    BRAS_NAME = "Bras"
    IN_PROM = "inProm"
    IN_MAX = "inMax"


class DailyReportFieldName:
    NAME = "name"
    TYPE = "type"
    CAPACITY = "capacity"
    DATE = "date"
    TYPE_LAYER = "typeLayer"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax"
    USE = "use"