import unittest
from datetime import datetime, timedelta
from concurrent.futures import Future
from unittest.mock import MagicMock, patch
from scanbackup.infrastructure.collectors.executer_scan import SCANScanner
from scanbackup.shared import DataImportError
from tests.support import TempDirTestCase

MODULE = "scanbackup.infrastructure.collectors.executer_scan"


class FakeExecutor:
    """Synchronous stand-in for ThreadPoolExecutor: runs submitted work inline."""

    instances: list["FakeExecutor"] = []

    def __init__(self, max_workers: int | None = None) -> None:
        self.max_workers = max_workers
        self.submissions: list[tuple] = []
        FakeExecutor.instances.append(self)

    def __enter__(self) -> "FakeExecutor":
        return self

    def __exit__(self, *args) -> bool:
        return False

    def submit(self, fn, *args, **kwargs) -> Future:
        self.submissions.append((fn, args, kwargs))
        future: Future = Future()
        try:
            future.set_result(fn(*args, **kwargs))
        except Exception as error:  # pragma: no cover - defensive
            future.set_exception(error)
        return future


def _make_source(interface: str, layer: str = "BORDE") -> MagicMock:
    """Build a lightweight stand-in for a TrafficSourceBBIPEntity."""
    source = MagicMock()
    source.interface = interface
    source.layer = layer
    return source


class TestSCANScanner(TempDirTestCase):
    """Unit tests for the pure-Python SCANScanner collector."""

    def setUp(self) -> None:
        super().setUp()
        SCANScanner._instance = None
        FakeExecutor.instances = []

    def tearDown(self) -> None:
        SCANScanner._instance = None
        super().tearDown()

    def _mock_config(self, max_workers: int = 5) -> MagicMock:
        """Build a fake Configuration exposing everything the scanner reads."""
        scan_credentials = MagicMock(username=" user ", password=" pass ")
        scanner = MagicMock(
            dir_storage="storage",
            dir_sources="sources",
            extension="csv",
            date_format="%Y-%m-%d",
            file_delimiter=";",
            port_separator_replacement="&",
            space_separator_replacement="_",
            max_workers=max_workers,
            scan_credentials=scan_credentials,
        )
        metadata = MagicMock(dir_data=str(self.tmp_dir), scanner=scanner)
        layers = MagicMock()
        layers.bbip.names = ["borde", "dint"]

        config = MagicMock()
        config.get_cfg_metadata.return_value = metadata
        config.get_cfg_layers.return_value = layers
        return config

    @patch(f"{MODULE}.Configuration")
    def test_initialize_creates_source_and_storage_dirs(self, mock_configuration) -> None:
        """initialize() must create the source and storage directories under dir_data."""
        mock_configuration.return_value = self._mock_config()

        scanner = SCANScanner()
        scanner.initialize(date="2026-01-02")

        self.assertTrue((self.tmp_dir / "sources").is_dir())
        self.assertTrue((self.tmp_dir / "storage").is_dir())
        self.assertEqual(scanner._date, "2026-01-02")

    @patch(f"{MODULE}.Configuration")
    def test_initialize_defaults_date_to_yesterday(self, mock_configuration) -> None:
        """Without an explicit date, initialize() must default to yesterday."""
        mock_configuration.return_value = self._mock_config()
        expected = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        scanner = SCANScanner()
        scanner.initialize()

        self.assertEqual(scanner._date, expected)

    @patch(f"{MODULE}.ScannerConfigError")
    @patch(f"{MODULE}.Configuration")
    def test_initialize_exits_on_config_failure(
        self, mock_configuration, mock_config_error
    ) -> None:
        """A configuration failure must be reported and terminate the process."""
        mock_configuration.side_effect = RuntimeError("boom")

        scanner = SCANScanner()
        with self.assertRaises(SystemExit) as ctx:
            scanner.initialize()
        self.assertEqual(ctx.exception.code, 1)
        mock_config_error.assert_called_once()

    @patch(f"{MODULE}.Configuration")
    def test_execute_layer_does_not_accumulate_across_calls(
        self, mock_configuration
    ) -> None:
        """Each execute_layer() call must replace _layers, not append to it (regression)."""
        mock_configuration.return_value = self._mock_config()
        scanner = SCANScanner()
        scanner.initialize()

        seen: list[list[str]] = []
        with patch.object(scanner, "_execute", side_effect=lambda: seen.append(list(scanner._layers))):
            scanner.execute_layer("BORDE")
            scanner.execute_layer("DINT")

        self.assertEqual(seen, [["BORDE"], ["DINT"]])

    @patch(f"{MODULE}.Configuration")
    def test_execute_all_uses_configured_bbip_layers(self, mock_configuration) -> None:
        """execute_all() must run every layer configured under layers.bbip.names."""
        mock_configuration.return_value = self._mock_config()
        scanner = SCANScanner()
        scanner.initialize()

        with patch.object(scanner, "_execute") as mock_execute:
            scanner.execute_all()

        self.assertEqual(scanner._layers, ["borde", "dint"])
        mock_execute.assert_called_once()

    @patch(f"{MODULE}.ScannerError")
    @patch(f"{MODULE}.TrafficSourceBBIPReader")
    @patch(f"{MODULE}.Configuration")
    def test_execute_layer_skips_missing_source_without_double_logging(
        self, mock_configuration, mock_reader_cls, mock_scanner_error
    ) -> None:
        """A missing/invalid source file already logs via DataImportError; must not be re-wrapped."""
        mock_configuration.return_value = self._mock_config()
        mock_reader_cls.return_value.import_data.side_effect = DataImportError()

        scanner = SCANScanner()
        scanner.initialize()
        scanner._execute_layer("BORDE")

        mock_scanner_error.assert_not_called()

    @patch(f"{MODULE}.ThreadPoolExecutor", new=FakeExecutor)
    @patch(f"{MODULE}.MRTGFetcher")
    @patch(f"{MODULE}.TrafficSourceBBIPReader")
    @patch(f"{MODULE}.Configuration")
    def test_execute_layer_dispatches_every_interface_using_configured_workers(
        self, mock_configuration, mock_reader_cls, mock_fetcher_cls
    ) -> None:
        """Every interface of the layer must be submitted to the pool sized by max_workers."""
        mock_configuration.return_value = self._mock_config(max_workers=3)
        sources = [_make_source(f"Gi0/0/{i}") for i in range(5)]
        mock_reader_cls.return_value.import_data.return_value = sources
        mock_fetcher_cls.return_value.fetch.return_value = []

        scanner = SCANScanner()
        scanner.initialize()
        scanner._execute_layer("BORDE")

        self.assertEqual(len(FakeExecutor.instances), 1)
        pool = FakeExecutor.instances[0]
        self.assertEqual(pool.max_workers, 3)
        self.assertEqual(len(pool.submissions), 5)

    @patch(f"{MODULE}.ThreadPoolExecutor", new=FakeExecutor)
    @patch(f"{MODULE}.ScannerError")
    @patch(f"{MODULE}.MRTGFetcher")
    @patch(f"{MODULE}.TrafficSourceBBIPReader")
    @patch(f"{MODULE}.Configuration")
    def test_a_single_interface_failure_does_not_abort_the_others(
        self,
        mock_configuration,
        mock_reader_cls,
        mock_fetcher_cls,
        mock_scanner_error,
    ) -> None:
        """A failing interface must be logged in isolation while its siblings still succeed."""
        mock_configuration.return_value = self._mock_config()
        ok_source = _make_source("Gi0/0/0")
        bad_source = _make_source("Gi0/0/1")
        mock_reader_cls.return_value.import_data.return_value = [ok_source, bad_source]

        def fetch(source, target_date):
            if source is bad_source:
                raise ConnectionError("network down")
            return ["row"]

        mock_fetcher_cls.return_value.fetch.side_effect = fetch

        scanner = SCANScanner()
        scanner.initialize()
        with patch.object(scanner, "_write_rows") as mock_write:
            scanner._execute_layer("BORDE")

        mock_write.assert_called_once()
        mock_scanner_error.assert_called_once()
        self.assertIn(bad_source.layer, mock_scanner_error.call_args.kwargs["layer"])

    def test_output_path_sanitizes_interface_name(self) -> None:
        """The storage filename must replace '/' and spaces per configuration."""
        scanner = SCANScanner()
        scanner._cfg_scanner = MagicMock(
            port_separator_replacement="&", space_separator_replacement="_"
        )
        scanner._dir_storage = self.tmp_dir

        path = scanner._output_path(" Gi 0/0/0 ")

        self.assertEqual(path.name, "Gi_0&0&0")

    def test_source_path_appends_configured_extension(self) -> None:
        """The source filename must append the configured extension."""
        scanner = SCANScanner()
        scanner._cfg_scanner = MagicMock(extension="csv")
        scanner._dir_sources = self.tmp_dir

        path = scanner._source_path("BORDE")

        self.assertEqual(path.name, "BORDE.csv")

    def test_write_rows_writes_header_only_on_new_file(self) -> None:
        """The header must be written once; further appends must not repeat it."""
        scanner = SCANScanner()
        scanner._cfg_scanner = MagicMock(file_delimiter=";")
        filepath = self.tmp_dir / "Gi0&0&0"

        scanner._write_rows(filepath, ["row-1"])
        scanner._write_rows(filepath, ["row-2"])

        content = filepath.read_text(encoding="utf-8").splitlines()
        self.assertEqual(content[0], scanner._get_header())
        self.assertEqual(content[1:], ["row-1", "row-2"])

    def test_write_rows_does_nothing_for_empty_rows(self) -> None:
        """No file should be created when there is no data to persist."""
        scanner = SCANScanner()
        scanner._cfg_scanner = MagicMock(file_delimiter=";")
        filepath = self.tmp_dir / "Gi0&0&0"

        scanner._write_rows(filepath, [])

        self.assertFalse(filepath.exists())


if __name__ == "__main__":
    unittest.main()
