from os import path


class PathConstant:
    """All paths neccessary to the system."""

    FILEPATH_LOGS = f"{path.realpath("./")}/system.log"
    SCAN_DATA_BORDER =   f"{path.realpath("./")}/data/SCAN/Borde"
    SCAN_DATA_BRAS =   f"{path.realpath("./")}/data/SCAN/Bras"
    SCAN_DATA_CACHING =   f"{path.realpath("./")}/data/SCAN/Caching"
    SCAN_DATA_RAI =   f"{path.realpath("./")}/data/SCAN/Rai"
