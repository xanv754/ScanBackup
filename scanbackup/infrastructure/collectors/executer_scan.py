import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from scanbackup.shared import (
    Configuration,
    LayerConfigModel,
    ScannerConfigModel,
    MetadataConfigModel,
    SCANHeader,
    LOG_HANDLER,
    ScannerError,
    ScannerConfigError,
)


class SCANScanner:
    _instance: "SCANScanner | None" = None
    _date: str
    _layers: list[str] = []
    _cfg_layers: LayerConfigModel
    _cfg_metadata: MetadataConfigModel
    _cfg_scanner: ScannerConfigModel
    _dir_data_tmp: Path
    _dir_data_src: Path
    _dir_tmp: Path
    _script_path: Path

    def __new__(cls) -> "SCANScanner":
        if not cls._instance:
            cls._instance = super(SCANScanner, cls).__new__(cls)
        return cls._instance

    def _setup_files_and_dirs(self) -> None:
        root = Path(
            Path(__file__).resolve().parent.parent.parent.parent
            / self._cfg_metadata.dir_data
        )
        self._script_path = Path(Path(__file__).resolve().parent / "scan.sh")
        self._dir_data_tmp = Path(root.resolve() / self._cfg_scanner.dir_storage)
        self._dir_data_tmp.mkdir(parents=True, exist_ok=True)
        self._dir_data_src = Path(root.resolve() / self._cfg_scanner.dir_sources)
        self._dir_data_src.mkdir(parents=True, exist_ok=True)
        self._dir_tmp = Path(root.resolve() / "tmp")
        if self._dir_tmp.exists():
            shutil.rmtree(self._dir_tmp)
        self._dir_tmp.mkdir(parents=True, exist_ok=True)

    def _set_date(self, date: str | None = None) -> None:
        if not date:
            date = datetime.now() - timedelta(days=1)
            date = date.strftime(self._cfg_scanner.date_format)
        self._date = date

    def _set_config(self) -> None:
        config = Configuration()
        self._cfg_metadata = config.get_cfg_metadata()
        self._cfg_scanner = self._cfg_metadata.scanner
        self._cfg_layers = config.get_cfg_layers()

    def _get_header(self) -> list[str]:
        header_str = ""
        for header in SCANHeader:
            header_str = header_str + header.value + self._cfg_scanner.file_delimiter
        header_str = header_str[:-1]
        return header_str

    def _source_exists(self, file_layer: str) -> bool:
        layer_source = Path(self._dir_data_src.resolve() / file_layer)
        return layer_source.is_file()

    def _execute(self) -> None:
        header_file = self._get_header()
        for layer in self._layers:
            layer = layer.upper().strip()
            if self._cfg_scanner.extension.strip() != "":
                layer = f"{layer}.{self._cfg_scanner.extension.strip()}"
            if not self._source_exists(layer):
                continue
            try:
                command = [
                    "bash",
                    self._script_path.resolve(),
                    self._date,
                    layer,
                    self._cfg_scanner.file_delimiter,
                    self._cfg_scanner.scan_credentials.username.strip(),
                    self._cfg_scanner.scan_credentials.password.strip(),
                    header_file,
                    self._dir_data_src,
                    self._dir_data_tmp,
                    self._dir_tmp,
                    LOG_HANDLER.filepath,
                    self._cfg_scanner.port_separator_replacement,
                    self._cfg_scanner.space_separator_replacement,
                    self._cfg_scanner.date_format,
                ]
                subprocess.run(command, capture_output=True, text=True)
            except Exception as error:
                ScannerError(error=error, layer=layer)
                continue

    def initialize(self, date: str | None = None) -> None:
        try:
            self._set_config()
            self._set_date(date)
            self._setup_files_and_dirs()
        except Exception as error:
            ScannerConfigError(error=error)
            exit(1)

    def execute_layer(self, layer_name: str) -> None:
        self._layers.append(layer_name)
        self._execute()

    def execute_all(self) -> None:
        self._layers = [layer.value for layer in self._cfg_layers.bbip.names]
        self._execute()
