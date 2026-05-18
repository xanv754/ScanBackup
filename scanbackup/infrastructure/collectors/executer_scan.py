import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from scanbackup.shared import (
    LayerBBIP,
    SCANHeader,
    PathConfig,
    ScanCredentialSchema,
    ScanCredentialEnvironment,
    SCANScannerError,
    SCANScannerConfigError,
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

    def _setup_directories(self) -> None:
        PathConfig.create_folder(PathConfig.FOLDER_LOG)
        PathConfig.create_folder(PathConfig.FOLDER_SOURCES)
        PathConfig.create_folder(PathConfig.FOLDER_BBIP_DATA)
        PathConfig.create_folder(PathConfig.FOLDER_TMP, empty=True)

    def _set_date(self, date: str | None = None) -> None:
        if not date:
            date = datetime.now() - timedelta(days=1)
            date = date.strftime(SCAN_COLLECTOR_FORMAT_DATE)
        self._date = date

    def _set_config(self, dev: bool = False) -> None:
        config = ScanCredentialEnvironment(dev=dev)
        self._credentials = config.get_credentials()

    def _get_header(self) -> list[str]:
        header_str = ""
        for header in SCANHeader:
            header_str = header_str + header.value + SCAN_COLLECTOR_SEPARATOR_FILE
        header_str = header_str[:-1]
        return header_str

    def _source_exists(self, layer: LayerBBIP) -> bool:
        layer_source = Path(PathConfig.FOLDER_SOURCES.resolve() / layer)
        return layer_source.is_file()

    def _execute(self) -> None:
        header_file = self._get_header()
        for layer in self._layers:
            layer = layer.upper()
            if not self._source_exists(layer):
                continue
            try:
                command = [
                    "bash",
                    PathConfig.SCAN_SCRIPT,
                    self._date,
                    layer,
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
                subprocess.run(command, capture_output=True, text=True)
            except Exception as error:
                SCANScannerError(error=error, layer=layer)
                continue

    def initialize(self, date: str | None = None, dev: bool = False) -> None:
        try:
            self._set_config(dev)
            self._set_date(date)
            self._setup_directories()
        except Exception as error:
            SCANScannerConfigError(error=error)
            exit(1)

    def execute_layer(self, layer_name: LayerBBIP) -> None:
        self._layers.append(layer_name)
        self._execute()

    def execute_all(self) -> None:
        self._layers = [layer.value for layer in LayerBBIP]
        self._execute()
