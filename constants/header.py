class HeaderDataFrame:
    """Header of the traffic dataframe."""
    ID = "id"
    NAME = "name"
    INTERFACE = "interface"
    CAPACITY = "capacity"
    MODEL = "model"
    TYPE = "type"
    SERVICE = "service"
    CREATE_AT = "createAt"
    DATE = "date"
    TIME = "time"
    ID_LAYER = "idLayer"
    TYPE_LAYER = "typeLayer"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax"
    IN_MAX_PROM = "inMaxProm"
    OUT_MAX_PROM = "outMaxProm"
    USE = "use (%)"


header_report_dialy = [
    HeaderDataFrame.INTERFACE,
    HeaderDataFrame.TYPE,
    HeaderDataFrame.DATE,
    HeaderDataFrame.CAPACITY,
    HeaderDataFrame.IN_PROM,
    HeaderDataFrame.OUT_PROM,
    HeaderDataFrame.IN_MAX,
    HeaderDataFrame.OUT_MAX,
    HeaderDataFrame.USE
]


header_dataframe = [
    HeaderDataFrame.INTERFACE,
    HeaderDataFrame.TYPE, 
    HeaderDataFrame.CAPACITY,
    HeaderDataFrame.DATE, 
    HeaderDataFrame.TIME,
    HeaderDataFrame.IN_PROM, 
    HeaderDataFrame.OUT_PROM, 
    HeaderDataFrame.IN_MAX, 
    HeaderDataFrame.OUT_MAX
]


header_summary = [
    HeaderDataFrame.INTERFACE,
    HeaderDataFrame.CAPACITY,
    HeaderDataFrame.IN_PROM,
    HeaderDataFrame.OUT_PROM,
    HeaderDataFrame.IN_MAX_PROM,
    HeaderDataFrame.OUT_MAX_PROM,
    HeaderDataFrame.USE
]