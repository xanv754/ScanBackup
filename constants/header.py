class HeaderConstant:
    """Header of the data file."""

    DATE = "Fecha"
    TIME = "Hora"
    IN_PROM = "InPro"
    OUT_PROM = "OutPro"
    IN_MAX = "InMax"
    OUT_MAX = "OutMax"


class HeaderTrafficDataFrameConstant:
    """Header of the traffic dataframe."""

    NAME = "interface"
    CAPACITY = "capacity"
    DATE = "date"
    TIME = "time"
    ID_LAYER = "idLayer"
    TYPE_LAYER = "typeLayer"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax"


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