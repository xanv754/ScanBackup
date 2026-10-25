from pathlib import Path

from interface_sync.constants.enums import TerminalLevel

TEXT_ENCODING = "utf-8"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LAYER_BORDE = "Borde"
LAYER_BRAS = "Bras"
LAYER_CACHING = "Caching"
LAYER_DINT = "Dint"
LAYER_DIST = "Dist"
LAYER_IXP = "Ixp"
LAYER_RAI = "Rai"

UNDEFINED_VENDOR = "Undefined"

FIELD_NAME = "name"
FIELD_SCAN_URL = "scan_url"
FIELD_CAPACITY_GBPS = "capacity_gbps"
FIELD_LABELS = {FIELD_NAME: "nombre", FIELD_SCAN_URL: "url"}

CONFIG_PATH_VARIABLE = "CONFIG_PATH"
DEFAULT_CONFIG_PATH = "/app/config.yml"
CONFIG_LINKS_KEY = "links"
ALLOWED_URL_SCHEMES = ("http", "https")

SCAN_USERNAME_VARIABLE = "SCAN_USERNAME"
SCAN_PASSWORD_VARIABLE = "SCAN_PASSWORD"

LOG_FILE_PATH = Path("/logs/interface-sync.log")
LOGGER_NAME = "interface_sync"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
LOG_DETAILS_SEPARATOR = " - "
LOG_ROTATION_DAY = "W5"
LOG_ROTATION_SUFFIX = "%Y-%m-%d"

TERMINAL_SPINNER_NAME = "dots"
TERMINAL_LEVEL_STYLES = {
    TerminalLevel.INFO: "green",
    TerminalLevel.WARNING: "yellow",
    TerminalLevel.ERROR: "red",
}
