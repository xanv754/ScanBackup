from enum import Enum
from scanbackup.shared.constants.headers.data_scan import SCANHeader


class TrafficHistoryBBIPHeader(str, Enum):
    DEVICE = "Device"
    INTERFACE = SCANHeader.INTERFACE.value
    DATE = SCANHeader.DATE.value
    TIME = SCANHeader.TIME.value
    IN_PROM = SCANHeader.IN_PROM.value
    OUT_PROM = SCANHeader.OUT_PROM.value
    IN_MAX = SCANHeader.IN_MAX.value
    OUT_MAX = SCANHeader.OUT_MAX.value
    LAYER = SCANHeader.LAYER.value
