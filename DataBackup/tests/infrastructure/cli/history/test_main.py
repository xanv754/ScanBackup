import unittest
from unittest.mock import patch
from click.testing import CliRunner
from scanbackup.infrastructure.cli.history.main import cli

MODULE = "scanbackup.infrastructure.cli.history.main"


class TestHistoryCli(unittest.TestCase):
    """Unit tests for the history CLI command wiring."""

    def setUp(self) -> None:
        """Build a Click test runner shared across assertions."""
        self.runner = CliRunner()

    @patch(f"{MODULE}.TrafficHistoryUpdater")
    def test_upload_delegates_with_given_options(self, mock_updater) -> None:
        """The 'upload' command must forward --date to TrafficHistoryUpdater."""
        result = self.runner.invoke(cli, ["upload", "--date", "2026-01-01"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str="2026-01-01")

    @patch(f"{MODULE}.TrafficHistoryUpdater")
    def test_upload_without_options_uses_defaults(self, mock_updater) -> None:
        """The 'upload' command must call TrafficHistoryUpdater with date_str=None when omitted."""
        result = self.runner.invoke(cli, ["upload"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str=None)

    @patch(f"{MODULE}.IPHistoryUpdater")
    def test_ip_upload_delegates_with_given_options(self, mock_updater) -> None:
        """The 'ip-upload' command must forward --date to IPHistoryUpdater."""
        result = self.runner.invoke(cli, ["ip-upload", "--date", "2026-01-01"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str="2026-01-01")

    @patch(f"{MODULE}.IPHistoryUpdater")
    def test_ip_upload_without_options_uses_defaults(self, mock_updater) -> None:
        """The 'ip-upload' command must call IPHistoryUpdater with date_str=None when omitted."""
        result = self.runner.invoke(cli, ["ip-upload"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str=None)


if __name__ == "__main__":
    unittest.main()
