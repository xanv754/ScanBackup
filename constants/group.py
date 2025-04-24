from database.constant.tables import TableNameDatabase


class ModelBordeType:
    """Model type for borde."""

    CISCO = 'CISCO'
    HUAWEI = 'HUAWEI'


class BrasType:
    """Type of bras."""

    UPLINK = 'UPLINK'
    DOWNLINK = 'DOWNLINK'

class LayerType:
    """Type of layer."""
    
    BORDE = TableNameDatabase.BORDE
    BRAS = TableNameDatabase.BRAS
    CACHING = TableNameDatabase.CACHING
    RAI = TableNameDatabase.RAI
    TRAFFIC_HISTORY = TableNameDatabase.TRAFFIC_HISTORY
    IP_HISTORY = TableNameDatabase.IP_HISTORY