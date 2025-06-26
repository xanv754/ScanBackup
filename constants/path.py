from os import path

class LayerNames:
    """All layers names."""

    BORDER = "Borde"
    BRAS = "Bras"
    CACHING = "Caching"
    IP_BRAS = "IPBras"
    RAI = "RAI"


layers_BBIP_SCAN = [
    LayerNames.BORDER,
    LayerNames.BRAS,
    LayerNames.CACHING,
    LayerNames.RAI
]


class DataPath:
    """All paths of the data system."""

    SCAN_DATA_BORDER = f"{path.abspath(__file__).split("/constants")[0]}/data/SCAN/Borde"
    SCAN_DATA_BRAS = f"{path.abspath(__file__).split("/constants")[0]}/data/SCAN/Bras"
    SCAN_DATA_CACHING = f"{path.abspath(__file__).split("/constants")[0]}/data/SCAN/Caching"
    SCAN_DATA_RAI = f"{path.abspath(__file__).split("/constants")[0]}/data/SCAN/RAI"
    SCAN_REPORT_DAILY = f"{path.abspath(__file__).split("/constants")[0]}/data/SCAN/Reportes-Diarios"


paths_BBIP_SCAN = [
    DataPath.SCAN_DATA_BORDER,
    DataPath.SCAN_DATA_BRAS,
    DataPath.SCAN_DATA_CACHING,
    DataPath.SCAN_DATA_RAI
]