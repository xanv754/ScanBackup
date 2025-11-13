class TableName:
    BORDE = "BORDE_HISTORY"
    BRAS = "BRAS_HISTORY"
    CACHING = "CACHING_HISTORY"
    RAI = "RAI_HISTORY"
    IP_BRAS_HISTORY = "IPBRAS_HISTORY"
    IXP = "IXP_HISTORY"
    DAILY_REPORT = "DAILY_SUMMARY_HISTORY"


class BBIPFieldName:
    NAME = "name"
    TYPE = "type"
    CAPACITY = "capacity"
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMaxProm"
    OUT_PROM = "outProm"
    OUT_MAX = "outMaxProm"


class IPBrasHistoryFieldName:
    DATE = "date"
    TIME = "time"
    BRAS_NAME = "brasname"
    IN_PROM = "inProm"
    IN_MAX = "inMaxProm"


class DailySummaryFieldName:
    NAME = "name"
    TYPE = "type"
    CAPACITY = "capacity"
    DATE = "date"
    TYPE_LAYER = "typeLayer"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMaxProm"
    OUT_MAX = "outMaxProm"
    USE = "use"
