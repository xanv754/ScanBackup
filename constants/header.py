class HeaderConstant:
    """Header of the data file."""

    DATE = "Fecha"
    TIME = "Hora"
    IN_PROM = "InPro"
    OUT_PROM = "OutPro"
    IN_MAX = "InMax"
    OUT_MAX = "OutMax"

class HeaderDataFrameConstant:
    """Header of the traffic dataframe."""
    ID = "id"
    NAME = "name"
    MODEL = "model"
    INTERFACE = "interface"
    CAPACITY = "capacity"
    DATE = "date"
    TIME = "time"
    ID_LAYER = "idLayer"
    TYPE_LAYER = "typeLayer"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax"
    TYPE = "type"
    SERVICE = "service"
    CREATE_AT = "createAt"


# class HeaderDataFrameConstant:
#     """Header of the traffic dataframe."""

#     NAME = "interface"
#     CAPACITY = "capacity"
#     DATE = "date"
#     TIME = "time"
#     ID_LAYER = "idLayer"
#     TYPE_LAYER = "typeLayer"
#     IN_PROM = "inProm"
#     OUT_PROM = "outProm"
#     IN_MAX = "inMax"
#     OUT_MAX = "outMax"
#     USE = "use (%)"


class HeaderBordeDataFrameConstant:
    """Header of the borde dataframe."""

    ID = "id"
    NAME = "name"
    MODEL = "model"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class HeaderBrasDataFrameConstant:
    """Header of the bras dataframe."""

    ID = "id"
    NAME = "name"
    TYPE = "type"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class HeaderCachingDataFrameConstant:
    """Header of the caching dataframe."""

    ID = "id"
    NAME = "name"
    SERVICE = "service"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class HeaderRaiDataFrameConstant:
    """Header of the rai dataframe."""

    ID = "id"
    NAME = "name"
    CAPACITY = "capacity"
    CREATE_AT = "createAt"


class HeaderSummaryDataFrameConstant:
    """Header of the summary dataframe."""

    INTERFACE = "interface"
    CAPACITY = "capacity"
    TYPE = "type"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX_PROM = "inMaxProm"
    OUT_MAX_PROM = "outMaxProm"
    USE = "use (%)"


header_summary = [
    HeaderSummaryDataFrameConstant.INTERFACE,
    HeaderSummaryDataFrameConstant.CAPACITY,
    HeaderSummaryDataFrameConstant.IN_PROM,
    HeaderSummaryDataFrameConstant.OUT_PROM,
    HeaderSummaryDataFrameConstant.IN_MAX_PROM,
    HeaderSummaryDataFrameConstant.OUT_MAX_PROM,
    HeaderSummaryDataFrameConstant.USE
]