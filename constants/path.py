from os import path


class DataPath:
    """All paths of the data system."""

    SCAN_DATA_BORDER = f"{path.abspath(__file__).split("/constants")[0]}/data/SCAN/Borde"
    SCAN_DATA_BRAS = f"{path.abspath(__file__).split("/constants")[0]}/data/SCAN/Bras"
    SCAN_DATA_CACHING = f"{path.abspath(__file__).split("/constants")[0]}/data/SCAN/Caching"
    SCAN_DATA_RAI = f"{path.abspath(__file__).split("/constants")[0]}/data/SCAN/RAI"
    SCAN_REPORT_DAILY = f"{path.abspath(__file__).split("/constants")[0]}/data/SCAN/Reportes-Diarios"