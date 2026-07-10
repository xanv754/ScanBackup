import unittest
from unittest.mock import patch
from click.testing import CliRunner
from scanbackup.application.cli.history.main import cli

MODULE = "scanbackup.application.cli.history.main"


class TestHistoryCli(unittest.TestCase):
    """Unit tests for the history CLI command wiring."""

    def setUp(self) -> None:
        """Build a Click test runner shared across assertions."""
        self.runner = CliRunner()

    @patch(f"{MODULE}.TrafficHistoryUpdater")
    def test_upload_delegates_with_given_options(self, mock_updater) -> None:
        """The 'upload' command must forward --layer and --date to TrafficHistoryUpdater."""
        result = self.runner.invoke(
            cli, ["upload", "--layer", "BORDE", "--date", "2026-01-01"]
        )
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(layer="BORDE", date_str="2026-01-01")

    def test_upload_requires_layer(self) -> None:
        """The 'upload' command must fail when --layer is not provided."""
        result = self.runner.invoke(cli, ["upload"])
        self.assertNotEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
