import unittest
from unittest.mock import patch
from click.testing import CliRunner
from scanbackup.application.cli.summaries.main import cli

MODULE = "scanbackup.application.cli.summaries.main"


class TestSummariesCli(unittest.TestCase):
    """Unit tests for the summaries CLI command wiring."""

    def setUp(self) -> None:
        """Build a Click test runner shared across assertions."""
        self.runner = CliRunner()

    @patch(f"{MODULE}.TrafficSummaryUpdater")
    def test_traffic_generate_delegates_with_given_options(self, mock_updater) -> None:
        """The 'traffic-generate' command must forward --date to TrafficSummaryUpdater."""
        result = self.runner.invoke(cli, ["traffic-generate", "--date", "2026-01-01"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str="2026-01-01")

    @patch(f"{MODULE}.TrafficSummaryUpdater")
    def test_traffic_generate_without_options_uses_defaults(self, mock_updater) -> None:
        """The 'traffic-generate' command must call TrafficSummaryUpdater with date_str=None when omitted."""
        result = self.runner.invoke(cli, ["traffic-generate"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str=None)

    @patch(f"{MODULE}.IPSummaryUpdater")
    def test_ip_generate_delegates_with_given_options(self, mock_updater) -> None:
        """The 'ip-generate' command must forward --date to IPSummaryUpdater."""
        result = self.runner.invoke(cli, ["ip-generate", "--date", "2026-01-01"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str="2026-01-01")

    @patch(f"{MODULE}.IPSummaryUpdater")
    def test_ip_generate_without_options_uses_defaults(self, mock_updater) -> None:
        """The 'ip-generate' command must call IPSummaryUpdater with date_str=None when omitted."""
        result = self.runner.invoke(cli, ["ip-generate"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str=None)

    @patch(f"{MODULE}.TrafficHourSummaryUpdater")
    def test_traffic_generate_hour_delegates_with_given_options(self, mock_updater) -> None:
        """The 'traffic-generate-hour' command must forward --date to TrafficHourSummaryUpdater."""
        result = self.runner.invoke(cli, ["traffic-generate-hour", "--date", "2026-01-01"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str="2026-01-01")

    @patch(f"{MODULE}.TrafficHourSummaryUpdater")
    def test_traffic_generate_hour_without_options_uses_defaults(self, mock_updater) -> None:
        """The 'traffic-generate-hour' command must call TrafficHourSummaryUpdater with date_str=None when omitted."""
        result = self.runner.invoke(cli, ["traffic-generate-hour"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str=None)

    @patch(f"{MODULE}.IPHourSummaryUpdater")
    def test_ip_generate_hour_delegates_with_given_options(self, mock_updater) -> None:
        """The 'ip-generate-hour' command must forward --date to IPHourSummaryUpdater."""
        result = self.runner.invoke(cli, ["ip-generate-hour", "--date", "2026-01-01"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str="2026-01-01")

    @patch(f"{MODULE}.IPHourSummaryUpdater")
    def test_ip_generate_hour_without_options_uses_defaults(self, mock_updater) -> None:
        """The 'ip-generate-hour' command must call IPHourSummaryUpdater with date_str=None when omitted."""
        result = self.runner.invoke(cli, ["ip-generate-hour"])
        self.assertEqual(result.exit_code, 0)
        mock_updater.execute.assert_called_once_with(date_str=None)


if __name__ == "__main__":
    unittest.main()
