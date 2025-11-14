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
    IN_PROM = "inProm"
    IN_MAX = "inMaxProm"
    OUT_PROM = "outProm"
    OUT_MAX = "outMaxProm"
    TYPE_LAYER = "typeLayer"


class HeaderIPBras:
    """Header of the Backbone IP dataframe."""

    BRAS_NAME = "brasname"
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMaxProm"
    CAPACITY = "capacity"


class HeaderDailySummary:
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
    HeaderBBIP.IN_PROM,
    HeaderBBIP.IN_MAX,
    HeaderBBIP.OUT_PROM,
    HeaderBBIP.OUT_MAX,
]

header_all_bbip = [
    HeaderBBIP.NAME,
    HeaderBBIP.TYPE,
    HeaderBBIP.CAPACITY,
    HeaderBBIP.DATE,
    HeaderBBIP.TIME,
    HeaderBBIP.IN_PROM,
    HeaderBBIP.IN_MAX,
    HeaderBBIP.OUT_PROM,
    HeaderBBIP.OUT_MAX,
    HeaderBBIP.TYPE_LAYER,
]

header_scan_bbip = [
    HeaderBBIP.DATE,
    HeaderBBIP.TIME,
    HeaderBBIP.IN_PROM,
    HeaderBBIP.IN_MAX,
    HeaderBBIP.OUT_PROM,
    HeaderBBIP.OUT_MAX,
]

header_ip_bras = [
    HeaderIPBras.DATE,
    HeaderIPBras.TIME,
    HeaderIPBras.IN_PROM,
    HeaderIPBras.IN_MAX,
    HeaderIPBras.BRAS_NAME, 
    HeaderIPBras.CAPACITY
]

header_scan_ip_bras = [
    HeaderIPBras.DATE,
    HeaderIPBras.TIME,
    HeaderIPBras.IN_PROM,
    HeaderIPBras.IN_MAX,
]

header_daily = [
    HeaderDailySummary.NAME,
    HeaderDailySummary.TYPE,
    HeaderDailySummary.CAPACITY,
    HeaderDailySummary.DATE,
    HeaderDailySummary.TYPE_LAYER,
    HeaderDailySummary.IN_PROM,
    HeaderDailySummary.OUT_PROM,
    HeaderDailySummary.IN_MAX,
    HeaderDailySummary.OUT_MAX,
    HeaderDailySummary.USE,
]

header_daily_bbip = [
    HeaderDailySummary.NAME,
    HeaderDailySummary.TYPE,
    HeaderDailySummary.DATE,
    HeaderDailySummary.CAPACITY,
    HeaderDailySummary.IN_PROM,
    HeaderDailySummary.OUT_PROM,
    HeaderDailySummary.IN_MAX,
    HeaderDailySummary.OUT_MAX,
    HeaderDailySummary.USE,
]

header_daily_ip_bras = [
    HeaderDailySummary.DATE,
    HeaderIPBras.BRAS_NAME,
    HeaderDailySummary.IN_PROM,
    HeaderDailySummary.IN_MAX,
]
