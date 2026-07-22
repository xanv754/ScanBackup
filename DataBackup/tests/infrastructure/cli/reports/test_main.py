import unittest
from unittest.mock import patch
from click.testing import CliRunner
from scanbackup.infrastructure.cli.reports.main import cli

MODULE = "scanbackup.infrastructure.cli.reports.main"


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
            month_str="2026-01", literal=False, output_dir="."
        )
        self.assertIn("/downloads/ScanBackup_2026-01.xlsx", result.output)

    @patch(f"{MODULE}.TrafficMonthlyReportGenerator")
    def test_monthly_traffic_without_options_uses_defaults(self, mock_generator) -> None:
        """The 'monthly-traffic' command must call TrafficMonthlyReportGenerator with None/False defaults when omitted."""
        mock_generator.execute.return_value = "/downloads/report.xlsx"

        result = self.runner.invoke(cli, ["monthly-traffic"])

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(
            month_str=None, literal=False, output_dir=None
        )

    @patch(f"{MODULE}.TrafficMonthlyReportGenerator")
    def test_monthly_traffic_literal_flag(self, mock_generator) -> None:
        """The 'monthly-traffic' command must forward --literal as True when given."""
        mock_generator.execute.return_value = "/downloads/report.xlsx"

        result = self.runner.invoke(cli, ["monthly-traffic", "--literal"])

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(
            month_str=None, literal=True, output_dir=None
        )

    @patch(f"{MODULE}.TrafficWeeklyReportGenerator")
    def test_weekly_traffic_delegates_with_given_options(self, mock_generator) -> None:
        """The 'weekly-traffic' command must forward --literal and --dirpath to TrafficWeeklyReportGenerator."""
        mock_generator.execute.return_value = "/downloads/ScanBackup_2026-01-05_2026-01-11.xlsx"

        result = self.runner.invoke(
            cli, ["weekly-traffic", "--literal", "--dirpath", "."]
        )

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(literal=True, output_dir=".")
        self.assertIn(
            "/downloads/ScanBackup_2026-01-05_2026-01-11.xlsx", result.output
        )

    @patch(f"{MODULE}.TrafficWeeklyReportGenerator")
    def test_weekly_traffic_without_options_uses_defaults(self, mock_generator) -> None:
        """The 'weekly-traffic' command must call TrafficWeeklyReportGenerator with literal=False, dirpath=None when omitted."""
        mock_generator.execute.return_value = "/downloads/report.xlsx"

        result = self.runner.invoke(cli, ["weekly-traffic"])

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(literal=False, output_dir=None)

    @patch(f"{MODULE}.TrafficBiweeklyReportGenerator")
    def test_biweekly_traffic_delegates_with_given_options(self, mock_generator) -> None:
        """The 'biweekly-traffic' command must forward --month, --literal and --dirpath to TrafficBiweeklyReportGenerator."""
        mock_generator.execute.return_value = "/downloads/ScanBackup_2026-01-01_2026-01-15.xlsx"

        result = self.runner.invoke(
            cli, ["biweekly-traffic", "--month", "2026-01", "--dirpath", "."]
        )

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(
            month_str="2026-01", literal=False, output_dir="."
        )
        self.assertIn(
            "/downloads/ScanBackup_2026-01-01_2026-01-15.xlsx", result.output
        )

    @patch(f"{MODULE}.TrafficBiweeklyReportGenerator")
    def test_biweekly_traffic_without_options_uses_defaults(self, mock_generator) -> None:
        """The 'biweekly-traffic' command must call TrafficBiweeklyReportGenerator with None/False defaults when omitted."""
        mock_generator.execute.return_value = "/downloads/report.xlsx"

        result = self.runner.invoke(cli, ["biweekly-traffic"])

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(
            month_str=None, literal=False, output_dir=None
        )

    @patch(f"{MODULE}.TrafficBiweeklyReportGenerator")
    def test_biweekly_traffic_literal_flag(self, mock_generator) -> None:
        """The 'biweekly-traffic' command must forward --literal as True when given."""
        mock_generator.execute.return_value = "/downloads/report.xlsx"

        result = self.runner.invoke(cli, ["biweekly-traffic", "--literal"])

        self.assertEqual(result.exit_code, 0)
        mock_generator.execute.assert_called_once_with(
            month_str=None, literal=True, output_dir=None
        )


if __name__ == "__main__":
    unittest.main()
