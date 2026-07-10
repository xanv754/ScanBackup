from unittest.mock import MagicMock, patch
from scanbackup.application.mappers.bbip.source_traffic import BBIPTrafficSourceMapper
from scanbackup.shared import ContentFileError
from tests.support import TempDirTestCase


class TestBBIPTrafficSourceMapper(TempDirTestCase):
    """Unit tests for the BBIPTrafficSourceMapper.from_csv conversion."""

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
    @patch("scanbackup.application.mappers.bbip.source_traffic.Configuration")
    def test_maps_rows_using_filename_as_layer(
        self, mock_configuration, mock_valid_layer
    ) -> None:
        """Every row must be converted into an entity tagged with the filename layer."""
        mock_configuration.return_value = self._mock_configuration()
        mock_valid_layer.return_value = True

        filepath = self.tmp_dir / "borde.csv"
        filepath.write_text(
            "link;enlace;capacidad;model\nhttp://example.com;Gi0/0/0;100.5;Cisco\n",
            encoding="utf-8",
        )

        sources = BBIPTrafficSourceMapper.from_csv(filepath)

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].layer, "BORDE")
        self.assertEqual(sources[0].capacity, 100.5)

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_bbip")
    @patch("scanbackup.application.mappers.bbip.source_traffic.Configuration")
    def test_invalid_row_raises_content_file_error(
        self, mock_configuration, mock_valid_layer
    ) -> None:
        """A row missing a required column must raise ContentFileError."""
        mock_configuration.return_value = self._mock_configuration()
        mock_valid_layer.return_value = True

        filepath = self.tmp_dir / "borde.csv"
        filepath.write_text("link;enlace\nhttp://example.com;Gi0/0/0\n", encoding="utf-8")

        with self.assertRaises(ContentFileError):
            BBIPTrafficSourceMapper.from_csv(filepath)


if __name__ == "__main__":
    import unittest

    unittest.main()
