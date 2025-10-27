class HeaderSource:
    """Header of the Source dataframe."""

    LINK = "link"
    NAME = "name"
    CAPACITY = "capacity"
    MODEL = "model"


class HeaderBBIP:
    """Header of the Backbone IP dataframe."""

    NAME = "name"
    TYPE = "type"
    CAPACITY = "capacity"
    DATE = "date"
    TIME = "time"
    IN_VALUE = "inValue"
    IN_MAX = "inMax"
    OUT_VALUE = "outValue"
    OUT_MAX = "outMax"
    TYPE_LAYER = "typeLayer"


class HeaderIPBras:
    """Header of the Backbone IP dataframe."""

    DATE = "date"
    TIME = "time"
    BRAS_NAME = "brasname"
    IN_PROM = "inProm"
    IN_MAX = "inMax"


class HeaderDailyReport:
    """Header of the Backbone IP dataframe."""

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


header_source = [
    HeaderSource.LINK,
    HeaderSource.NAME,
    HeaderSource.CAPACITY,
    HeaderSource.MODEL,
]

header_bbip = [
    HeaderBBIP.NAME,
    HeaderBBIP.TYPE,
    HeaderBBIP.CAPACITY,
    HeaderBBIP.DATE,
    HeaderBBIP.TIME,
    HeaderBBIP.IN_VALUE,
    HeaderBBIP.IN_MAX,
    HeaderBBIP.OUT_VALUE,
    HeaderBBIP.OUT_MAX,
]

header_all_bbip = [
    HeaderBBIP.NAME,
    HeaderBBIP.TYPE,
    HeaderBBIP.CAPACITY,
    HeaderBBIP.DATE,
    HeaderBBIP.TIME,
    HeaderBBIP.IN_VALUE,
    HeaderBBIP.IN_MAX,
    HeaderBBIP.OUT_VALUE,
    HeaderBBIP.OUT_MAX,
    HeaderBBIP.TYPE_LAYER,
]

header_upload_scan_data = [
    HeaderBBIP.DATE,
    HeaderBBIP.TIME,
    HeaderBBIP.IN_VALUE,
    HeaderBBIP.IN_MAX,
    HeaderBBIP.OUT_VALUE,
    HeaderBBIP.OUT_MAX,
]

header_ip_bras = [
    HeaderIPBras.DATE,
    HeaderIPBras.TIME,
    HeaderIPBras.IN_PROM,
    HeaderIPBras.IN_MAX,
]

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
    HeaderDailyReport.USE,
]

header_upload_daily_data = [
    HeaderDailyReport.NAME,
    HeaderDailyReport.TYPE,
    HeaderDailyReport.DATE,
    HeaderDailyReport.CAPACITY,
    HeaderDailyReport.IN_PROM,
    HeaderDailyReport.OUT_PROM,
    HeaderDailyReport.IN_MAX,
    HeaderDailyReport.OUT_MAX,
    HeaderDailyReport.USE,
]
