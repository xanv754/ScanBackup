import unittest
from unittest.mock import patch
from scanbackup.shared.errors.system import ScanBackupError, ModuleSystem


@patch("scanbackup.shared.errors.system.Terminal")
@patch("scanbackup.shared.errors.system.Log")
class TestScanBackupError(unittest.TestCase):
    """Unit tests for the ScanBackupError base exception."""

    def test_message_without_error_or_module(self, mock_log, mock_terminal) -> None:
        """A plain message must be kept as-is and module default to 'System'."""
        error = ScanBackupError(message="Something failed")
        self.assertEqual(str(error), "Something failed")
        self.assertEqual(error.module, "System")

    def test_message_with_module(self, mock_log, mock_terminal) -> None:
        """Passing a module must set the human-readable module label."""
        error = ScanBackupError(message="Something failed", module=ModuleSystem.MONGO)
        self.assertEqual(error.module, ModuleSystem.MONGO.value)

    def test_message_with_wrapped_error(self, mock_log, mock_terminal) -> None:
        """A wrapped error must be appended to the final message."""
        error = ScanBackupError(message="Something failed", error=ValueError("boom"))
        self.assertIn("Something failed", str(error))
        self.assertIn("boom", str(error))

    def test_logs_and_prints_on_construction(self, mock_log, mock_terminal) -> None:
        """Constructing the error must emit both a log entry and a terminal message."""
        ScanBackupError(message="Something failed", module=ModuleSystem.DATABASE)
        mock_log.error.assert_called_once()
        mock_terminal.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
