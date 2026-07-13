from unittest.mock import MagicMock, patch
from scanbackup.infrastructure.readers.csv.sources.data import (
    TrafficSourceBBIPReader,
    IPSourceBBIPReader,
)
from scanbackup.shared import DataImportError, LayerNotDefined
from tests.support import TempDirTestCase


class TestTrafficSourceBBIPReader(TempDirTestCase):
    """Unit tests for the TrafficSourceBBIPReader CSV reader."""

    def _mock_configuration(self) -> MagicMock:
        """Build a fake Configuration exposing the scanner file delimiter."""
        scanner = MagicMock()
        scanner.file_delimiter = ";"
        metadata = MagicMock()
        metadata.scanner = scanner
        config = MagicMock()
        config.get_cfg_metadata.return_value = metadata
        return config

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_bbip")
    @patch("scanbackup.infrastructure.readers.csv.sources.data.Configuration")
    def test_imports_entities_using_filename_as_layer(
        self, mock_configuration, mock_valid_layer
    ) -> None:
        """The layer must be taken from the filename and applied to every row."""
        mock_configuration.return_value = self._mock_configuration()
        mock_valid_layer.return_value = True

        filepath = self.tmp_dir / "borde.csv"
        filepath.write_text(
            "link;enlace;capacidad;model\n"
            "http://example.com;Gi0/0/0;100.5;Cisco\n",
            encoding="utf-8",
        )

        reader = TrafficSourceBBIPReader()
        sources = reader.import_data(filepath)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].layer, "BORDE")
        self.assertEqual(sources[0].capacity, 100.5)

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_bbip")
    @patch("scanbackup.infrastructure.readers.csv.sources.data.Configuration")
    def test_undefined_layer_raises_data_import_error(
        self, mock_configuration, mock_valid_layer
    ) -> None:
        """An unrecognized layer (derived from the filename) must fail the import."""
        mock_configuration.return_value = self._mock_configuration()
        mock_valid_layer.return_value = False

        filepath = self.tmp_dir / "unknown.csv"
        filepath.write_text("link;enlace;capacidad;model\n", encoding="utf-8")

        reader = TrafficSourceBBIPReader()
        with self.assertRaises(DataImportError) as ctx:
            reader.import_data(filepath)
        self.assertIsInstance(ctx.exception.error, LayerNotDefined)


class TestIPSourceBBIPReader(TempDirTestCase):
    """Unit tests for the IPSourceBBIPReader CSV reader."""

    def _mock_configuration(self) -> MagicMock:
        """Build a fake Configuration exposing the scanner file delimiter."""
        scanner = MagicMock()
        scanner.file_delimiter = ";"
        metadata = MagicMock()
        metadata.scanner = scanner
        config = MagicMock()
        config.get_cfg_metadata.return_value = metadata
        return config

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_ip")
    @patch("scanbackup.infrastructure.readers.csv.sources.data.Configuration")
    def test_imports_entities_using_filename_as_layer(
        self, mock_configuration, mock_valid_layer
    ) -> None:
        """The layer must be taken from the filename and applied to every row."""
        mock_configuration.return_value = self._mock_configuration()
        mock_valid_layer.return_value = True

        filepath = self.tmp_dir / "brasip.csv"
        filepath.write_text(
            "link;interface\nhttp://example.com;BRAS-00\n",
            encoding="utf-8",
        )

        reader = IPSourceBBIPReader()
        sources = reader.import_data(filepath)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].layer, "BRASIP")
        self.assertEqual(sources[0].interface, "BRAS-00")
        self.assertEqual(sources[0].link, "http://example.com")

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_ip")
    @patch("scanbackup.infrastructure.readers.csv.sources.data.Configuration")
    def test_undefined_layer_raises_data_import_error(
        self, mock_configuration, mock_valid_layer
    ) -> None:
        """An unrecognized layer (derived from the filename) must fail the import."""
        mock_configuration.return_value = self._mock_configuration()
        mock_valid_layer.return_value = False

        filepath = self.tmp_dir / "unknown.csv"
        filepath.write_text("link;interface\n", encoding="utf-8")

        reader = IPSourceBBIPReader()
        with self.assertRaises(DataImportError) as ctx:
            reader.import_data(filepath)
        self.assertIsInstance(ctx.exception.error, LayerNotDefined)


if __name__ == "__main__":
    import unittest

    unittest.main()
