import unittest
from unittest.mock import patch
from scanbackup.shared.errors.export_error import (
    ExportError,
    ExcelExportError,
    CSVExportError,
)


@patch("scanbackup.shared.errors.system.Terminal")
@patch("scanbackup.shared.errors.system.Log")
class TestExportError(unittest.TestCase):
    """Unit tests for the export error hierarchy."""

    def test_export_error_includes_filename(self, mock_log, mock_terminal) -> None:
        """ExportError must include the failed filename when provided."""
        error = ExportError(filename="report.csv")
        self.assertIn("report.csv", str(error))

    def test_excel_export_error_includes_filename(self, mock_log, mock_terminal) -> None:
        """ExcelExportError must include the failed filename when provided."""
        error = ExcelExportError(filename="report.xlsx")
        self.assertIn("report.xlsx", str(error))
        self.assertIn("excel", str(error))

    def test_csv_export_error_includes_filename(self, mock_log, mock_terminal) -> None:
        """CSVExportError must include the failed filename when provided."""
        error = CSVExportError(filename="report.csv")
        self.assertIn("report.csv", str(error))
        self.assertIn(".csv", str(error))


if __name__ == "__main__":
    unittest.main()
