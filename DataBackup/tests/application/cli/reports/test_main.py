import unittest
from unittest.mock import patch
from click.testing import CliRunner
from scanbackup.application.cli.reports.main import cli

MODULE = "scanbackup.application.cli.reports.main"


class TestReportsCli(unittest.TestCase):
    """Unit tests for the reports CLI command wiring."""

    def setUp(self) -> None:
        """Build a Click test runner shared across assertions."""
        self.runner = CliRunner()

    @patch(f"{MODULE}.TrafficDailyReportGenerator")
    def test_daily_traffic_delegates_with_given_options(self, mock_generator) -> None:
        """The 'daily-traffic' command must forward --date and --dirpath to TrafficDailyReportGenerator."""
        mock_generator.execute.return_value = "/downloads/ScanBackup_2026-01-01.xlsx"

        result = self.runner.invoke(
            cli, ["daily-traffic", "--date", "2026-01-01", "--dirpath", "."]
        )

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(
            date_str="2026-01-01", output_dir="."
        )
        self.assertIn("/downloads/ScanBackup_2026-01-01.xlsx", result.output)

    @patch(f"{MODULE}.TrafficDailyReportGenerator")
    def test_daily_traffic_without_options_uses_defaults(self, mock_generator) -> None:
        """The 'daily-traffic' command must call TrafficDailyReportGenerator with None defaults when omitted."""
        mock_generator.execute.return_value = "/downloads/report.xlsx"

        result = self.runner.invoke(cli, ["daily-traffic"])

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(date_str=None, output_dir=None)

    @patch(f"{MODULE}.TrafficMonthlyReportGenerator")
    def test_monthly_traffic_delegates_with_given_options(self, mock_generator) -> None:
        """The 'monthly-traffic' command must forward --month and --dirpath to TrafficMonthlyReportGenerator."""
        mock_generator.execute.return_value = "/downloads/ScanBackup_2026-01.xlsx"

        result = self.runner.invoke(
            cli, ["monthly-traffic", "--month", "2026-01", "--dirpath", "."]
        )

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(
            month_str="2026-01", output_dir="."
        )
        self.assertIn("/downloads/ScanBackup_2026-01.xlsx", result.output)

    @patch(f"{MODULE}.TrafficMonthlyReportGenerator")
    def test_monthly_traffic_without_options_uses_defaults(self, mock_generator) -> None:
        """The 'monthly-traffic' command must call TrafficMonthlyReportGenerator with None defaults when omitted."""
        mock_generator.execute.return_value = "/downloads/report.xlsx"

        result = self.runner.invoke(cli, ["monthly-traffic"])

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(month_str=None, output_dir=None)


if __name__ == "__main__":
    unittest.main()
