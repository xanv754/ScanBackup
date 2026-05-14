import subprocess
from datetime import datetime, timedelta
from scanbackup.shared import (
    LayerBBIP,
    SCANHeader,
    PathConfig,
    ScanCredentialSchema,
    ScanCredentialEnvironment,
    REPLACE_SYMBOL_SPACE,
    REPLACE_SYMBOL_PORTS,
    SCAN_COLLECTOR_FORMAT_DATE,
    SCAN_COLLECTOR_SEPARATOR_FILE,
)


class SCANScanner:
    _instance: "SCANScanner | None" = None
    _date: str
    _layers: list[str] = []
    _credentials: ScanCredentialSchema

    def __new__(cls) -> "SCANScanner":
        if not cls._instance:
            cls._instance = super(SCANScanner, cls).__new__(cls)
        return cls._instance

    def __init__(self, date: str | None = None) -> None:
        if not hasattr(self, "_attr"):
            config = ScanCredentialEnvironment()
            self._credentials = config.get_credentials()
            self._setup_directories()
            self._declare_date(date)

    def _setup_directories(self) -> None:
        PathConfig.create_folder(PathConfig.FOLDER_LOG)
        PathConfig.create_folder(PathConfig.FOLDER_SOURCES)
        PathConfig.create_folder(PathConfig.FOLDER_BBIP_DATA)
        PathConfig.create_folder(PathConfig.FOLDER_TMP, empty=True)

    def _declare_date(self, date: str | None = None) -> None:
        if not date:
            date = datetime.now() - timedelta(days=1)
            date = date.strftime(SCAN_COLLECTOR_FORMAT_DATE)
        self._date = date

    def _get_header(self) -> list[str]:
        header_str = ""
        for header in SCANHeader:
            header_str = header.value + SCAN_COLLECTOR_SEPARATOR_FILE
        header_str = header_str[:-1]
        return header_str

    def _execute(self) -> None:
        header_file = self._get_header()
        command = [
            "bash",
            PathConfig.SCAN_SCRIPT,
            self._date,
            self._layers,
            SCAN_COLLECTOR_SEPARATOR_FILE,
            self._credentials.username.strip(),
            self._credentials.password.strip(),
            header_file,
            PathConfig.FOLDER_SOURCES.resolve(),
            PathConfig.FOLDER_BBIP_DATA.resolve(),
            PathConfig.FOLDER_TMP.resolve(),
            PathConfig.LOG_FILE.resolve(),
            REPLACE_SYMBOL_PORTS,
            REPLACE_SYMBOL_SPACE,
            SCAN_COLLECTOR_FORMAT_DATE,
        ]
        process = subprocess.run(command, capture_output=True, text=True)

    def execute_layer(self, layer_name: LayerBBIP) -> None:
        self._layers.append(layer_name)
        pass

    def execute_all(self) -> None:
        self._layers = [layer.value for layer in LayerBBIP]
        pass
