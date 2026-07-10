from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from scanbackup.domain import TrafficSourceBBIPEntity
from scanbackup.infrastructure.readers.csv.sources.data import TrafficSourceBBIPReader
from scanbackup.infrastructure.collectors.mrtg_fetcher import MRTGFetcher
from scanbackup.shared import (
    Configuration,
    LayerConfigModel,
    ScannerConfigModel,
    MetadataConfigModel,
    SCANHeader,
    DataImportError,
    ScannerError,
    ScannerConfigError,
)


class SCANScanner:
    _instance: "SCANScanner | None" = None
    _date: str
    _layers: list[str]
    _cfg_layers: LayerConfigModel
    _cfg_metadata: MetadataConfigModel
    _cfg_scanner: ScannerConfigModel
    _dir_sources: Path
    _dir_storage: Path

    def __new__(cls) -> "SCANScanner":
        if not cls._instance:
            cls._instance = super(SCANScanner, cls).__new__(cls)
        return cls._instance

    def _setup_files_and_dirs(self) -> None:
        """Resolve and create the source and storage directories used by the scanner."""
        root = Path(
            Path(__file__).resolve().parent.parent.parent.parent
            / self._cfg_metadata.dir_data
        )
        self._dir_storage = Path(root.resolve() / self._cfg_scanner.dir_storage)
        self._dir_storage.mkdir(parents=True, exist_ok=True)
        self._dir_sources = Path(root.resolve() / self._cfg_scanner.dir_sources)
        self._dir_sources.mkdir(parents=True, exist_ok=True)

    def _set_date(self, date: str | None = None) -> None:
        """Resolve the target date to collect, defaulting to yesterday."""
        if not date:
            current_date = datetime.now() - timedelta(days=1)
            date = current_date.strftime(self._cfg_scanner.date_format)
        self._date = date

    def _set_config(self) -> None:
        """Load and cache the system configuration sections used by the scanner."""
        config = Configuration()
        self._cfg_metadata = config.get_cfg_metadata()
        self._cfg_scanner = self._cfg_metadata.scanner
        self._cfg_layers = config.get_cfg_layers()

    def _get_header(self) -> str:
        """Build the delimited header line written at the top of every output file."""
        return self._cfg_scanner.file_delimiter.join(
            header.value for header in SCANHeader
        )

    def _source_path(self, layer: str) -> Path:
        """Resolve the source CSV filepath of a layer."""
        filename = layer
        if self._cfg_scanner.extension.strip() != "":
            filename = f"{layer}.{self._cfg_scanner.extension.strip()}"
        return Path(self._dir_sources.resolve() / filename)

    def _output_path(self, interface: str) -> Path:
        """Resolve the storage filepath of an interface, sanitizing its name."""
        filename = (
            interface.strip()
            .replace("/", self._cfg_scanner.port_separator_replacement)
            .replace(" ", self._cfg_scanner.space_separator_replacement)
        )
        return Path(self._dir_storage.resolve() / filename)

    def _write_rows(self, filepath: Path, rows: list[str]) -> None:
        """Append rows to filepath, writing the header first if the file is new or empty."""
        if not rows:
            return
        is_new = not filepath.exists() or filepath.stat().st_size == 0
        with filepath.open("a", encoding="utf-8") as f:
            if is_new:
                f.write(self._get_header() + "\n")
            f.write("\n".join(rows) + "\n")

    def _process_interface(
        self, fetcher: MRTGFetcher, source: TrafficSourceBBIPEntity
    ) -> None:
        """Fetch and persist a single interface's traffic data, isolating its failures."""
        try:
            rows = fetcher.fetch(source, self._date)
            self._write_rows(self._output_path(source.interface), rows)
        except Exception as error:
            ScannerError(error=error, layer=f"{source.layer}/{source.interface}")

    def _execute_layer(self, layer: str) -> None:
        """Collect the traffic of every interface of a layer, `max_workers` at a time."""
        layer = layer.upper().strip()
        try:
            sources = TrafficSourceBBIPReader().import_data(self._source_path(layer))
        except DataImportError:
            return
        if not sources:
            return

        fetcher = MRTGFetcher(
            username=self._cfg_scanner.scan_credentials.username.strip(),
            password=self._cfg_scanner.scan_credentials.password.strip(),
            delimiter=self._cfg_scanner.file_delimiter,
            date_format=self._cfg_scanner.date_format,
        )
        with ThreadPoolExecutor(max_workers=self._cfg_scanner.max_workers) as executor:
            futures = [
                executor.submit(self._process_interface, fetcher, source)
                for source in sources
            ]
            for future in as_completed(futures):
                future.result()

    def _execute(self) -> None:
        """Run the collection process for every layer requested in this run."""
        for layer in self._layers:
            try:
                self._execute_layer(layer)
            except Exception as error:
                ScannerError(error=error, layer=layer)
                continue

    def initialize(self, date: str | None = None) -> None:
        """Load configuration, resolve the target date and prepare filesystem paths."""
        try:
            self._layers = []
            self._set_config()
            self._set_date(date)
            self._setup_files_and_dirs()
        except Exception as error:
            ScannerConfigError(error=error)
            exit(1)

    def execute_layer(self, layer_name: str) -> None:
        """Run the collection process for a single layer."""
        self._layers = [layer_name]
        self._execute()

    def execute_all(self) -> None:
        """Run the collection process for every layer configured under `layers.bbip`."""
        self._layers = [layer for layer in self._cfg_layers.bbip.names]
        self._execute()
