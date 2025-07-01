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


class HeaderBBIP:
    """Header of the Backbone IP dataframe."""
    NAME = "name"
    TYPE = "type"
    CAPACITY = "capacity"
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    OUT_PROM = "outProm"
    OUT_MAX = "outMax"


header_bbip = [
    HeaderBBIP.NAME,
    HeaderBBIP.TYPE,
    HeaderBBIP.CAPACITY,
    HeaderBBIP.DATE,
    HeaderBBIP.TIME,
    HeaderBBIP.IN_PROM,
    HeaderBBIP.IN_MAX,
    HeaderBBIP.OUT_PROM,
    HeaderBBIP.OUT_MAX
]

header_upload_scan_data = [
    HeaderBBIP.DATE,
    HeaderBBIP.TIME,
    HeaderBBIP.IN_PROM,
    HeaderBBIP.IN_MAX,
    HeaderBBIP.OUT_PROM,
    HeaderBBIP.OUT_MAX
]

class HeaderIPBras:
    """Header of the Backbone IP dataframe."""
    DATE = "date"
    TIME = "time"
    BRAS_NAME = "Bras"
    IN_PROM = "inProm"
    IN_MAX = "inMax"


header_ip_bras = [
    HeaderIPBras.DATE,
    HeaderIPBras.TIME,
    HeaderIPBras.BRAS_NAME,
    HeaderIPBras.IN_PROM,
    HeaderIPBras.IN_MAX
]


class HeaderDailyReport:
    """Header of the Backbone IP dataframe."""
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


header_daily_report = [
    HeaderDailyReport.NAME,
    HeaderDailyReport.TYPE,
    HeaderDailyReport.CAPACITY,
    HeaderDailyReport.DATE,
    HeaderDailyReport.TYPE_LAYER,
    HeaderDailyReport.IN_PROM,
    HeaderDailyReport.OUT_PROM,
    HeaderDailyReport.IN_MAX,
    HeaderDailyReport.OUT_MAX,
    HeaderDailyReport.USE
]

header_upload_daily_data = [
    HeaderDailyReport.NAME,
    HeaderDailyReport.TYPE,
    HeaderDailyReport.CAPACITY,
    HeaderDailyReport.DATE,
    HeaderDailyReport.IN_PROM,
    HeaderDailyReport.OUT_PROM,
    HeaderDailyReport.IN_MAX,
    HeaderDailyReport.OUT_MAX,
    HeaderDailyReport.USE
]