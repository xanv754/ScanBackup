import unittest
from unittest.mock import patch
from scanbackup.shared.errors.scanner_error import ScannerError, ScannerConfigError


@patch("scanbackup.shared.errors.system.Terminal")
@patch("scanbackup.shared.errors.system.Log")
class TestScannerError(unittest.TestCase):
    """Unit tests for the scanner error hierarchy."""

    def test_scanner_error_default_message(self, mock_log, mock_terminal) -> None:
        """ScannerError without a message must use the default text."""
        error = ScannerError()
        self.assertIn("SCAN", str(error))

    def test_scanner_error_includes_layer(self, mock_log, mock_terminal) -> None:
        """ScannerError must include the failing layer when provided."""
        error = ScannerError(layer="BORDE")
        self.assertIn("BORDE", str(error))

    def test_scanner_config_error_default_message(self, mock_log, mock_terminal) -> None:
        """ScannerConfigError must always report the fixed configuration failure text."""
        error = ScannerConfigError()
        self.assertIn("configuración", str(error))


if __name__ == "__main__":
    unittest.main()
