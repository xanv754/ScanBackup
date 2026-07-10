import csv
from unittest.mock import MagicMock, patch
from pydantic import BaseModel
from scanbackup.infrastructure.writers.csv.export import CSVWriter
from scanbackup.shared import CSVExportError
from tests.support import TempDirTestCase


class _Item(BaseModel):
    """Minimal pydantic model used to exercise CSVWriter.export."""

    name: str
    value: int


class TestCSVWriter(TempDirTestCase):
    """Unit tests for the CSVWriter.export method."""

    def _mock_configuration(self) -> MagicMock:
        """Build a fake Configuration exposing the scanner file delimiter."""
        scanner = MagicMock()
        scanner.file_delimiter = ";"
        metadata = MagicMock()
        metadata.scanner = scanner
        config = MagicMock()
        config.get_cfg_metadata.return_value = metadata
        return config

    @patch("scanbackup.infrastructure.writers.csv.export.Configuration")
    def test_writes_csv_and_returns_filepath(self, mock_configuration) -> None:
        """export() must write every row and return the resolved output path."""
        mock_configuration.return_value = self._mock_configuration()
        writer = CSVWriter(dir=self.tmp_dir)

        result = writer.export(filename="items", data=[_Item(name="a", value=1)])

        expected_path = self.tmp_dir / "items.csv"
        self.assertEqual(result, str(expected_path.resolve()))
        with expected_path.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter=";"))
        self.assertEqual(rows, [{"name": "a", "value": "1"}])

    @patch("scanbackup.infrastructure.writers.csv.export.Configuration")
    def test_excludes_given_fields(self, mock_configuration) -> None:
        """export() must omit excluded fields from the written rows."""
        mock_configuration.return_value = self._mock_configuration()
        writer = CSVWriter(dir=self.tmp_dir)

        writer.export(
            filename="items", data=[_Item(name="a", value=1)], exclude={"value"}
        )

        expected_path = self.tmp_dir / "items.csv"
        with expected_path.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter=";"))
        self.assertEqual(rows, [{"name": "a"}])

    @patch("scanbackup.infrastructure.writers.csv.export.Configuration")
    def test_empty_data_raises_csv_export_error(self, mock_configuration) -> None:
        """Exporting an empty dataset must be wrapped into CSVExportError."""
        mock_configuration.return_value = self._mock_configuration()
        writer = CSVWriter(dir=self.tmp_dir)

        with self.assertRaises(CSVExportError):
            writer.export(filename="items", data=[])


if __name__ == "__main__":
    import unittest

    unittest.main()
