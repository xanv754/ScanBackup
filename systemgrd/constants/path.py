from os import path


class DataPath:
    """All paths of the data system."""

    ROOT_PATH = path.abspath(path.join(path.dirname(__file__), "..", ".."))
    SCAN_DATA_BORDE = path.join(ROOT_PATH, "data", "SCAN", "Borde")
    SCAN_DATA_BRAS = path.join(ROOT_PATH, "data", "SCAN", "Bras")
    SCAN_DATA_CACHING = path.join(ROOT_PATH, "data", "SCAN", "Caching")
    SCAN_DATA_RAI = path.join(ROOT_PATH, "data", "SCAN", "Rai")
    SCAN_DATA_IXP = path.join(ROOT_PATH, "data", "SCAN", "IXP")
    SCAN_DATA_IPBRAS = path.join(ROOT_PATH, "data", "SCAN", "IPBras")
    SCAN_REPORT_DAILY = path.join(ROOT_PATH, "data", "SCAN", "Reportes-Diarios")
    SCAN_SOURCES = path.join(ROOT_PATH, "sources", "SCAN")
    SCAN_SOURCES_BK = path.join(ROOT_PATH, "sources", "BK_SCAN")


paths_BBIP_SCAN = [
    DataPath.SCAN_DATA_BORDE,
    DataPath.SCAN_DATA_BRAS,
    DataPath.SCAN_DATA_CACHING,
    DataPath.SCAN_DATA_RAI,
]


if __name__ == "__main__":
    print(DataPath.SCAN_DATA_BORDE)
    print(DataPath.SCAN_DATA_BRAS)
    print(DataPath.SCAN_DATA_CACHING)
    print(DataPath.SCAN_DATA_RAI)
    print(DataPath.SCAN_REPORT_DAILY)
    print(DataPath.SCAN_SOURCES)
