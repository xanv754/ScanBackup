import unittest
from unittest.mock import patch
from scanbackup.shared.errors.updater_error import UpdaterError


@patch("scanbackup.shared.errors.system.Terminal")
@patch("scanbackup.shared.errors.system.Log")
class TestUpdaterError(unittest.TestCase):
    """Unit tests for the UpdaterError exception."""

    def test_default_message(self, mock_log, mock_terminal) -> None:
        """UpdaterError without a message must use the default text."""
        error = UpdaterError()
        self.assertIn("actualización", str(error))

    def test_includes_layer(self, mock_log, mock_terminal) -> None:
        """UpdaterError must include the failing layer when provided."""
        error = UpdaterError(layer="DINT")
        self.assertIn("DINT", str(error))


if __name__ == "__main__":
    unittest.main()
