import unittest
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.reports.generator import (
    TrafficDailyReportGenerator,
    TrafficMonthlyReportGenerator,
)

MODULE = "scanbackup.application.cli.reports.generator"


class TestTrafficDailyReportGenerator(unittest.TestCase):
    """Unit tests for the TrafficDailyReportGenerator CLI orchestration class."""

    def _mock_configuration(self, mock_configuration, names: list[str]) -> MagicMock:
        """Wire a fake Configuration exposing the configured bbip layer names and report prefix."""
        layers = MagicMock()
        layers.bbip.names = names
        reports = MagicMock()
        reports.preffix_name = "ScanBackup"
        metadata = MagicMock()
        metadata.reports = reports
        config = mock_configuration.return_value
        config.get_cfg_layers.return_value = layers
        config.get_cfg_metadata.return_value = metadata
        return config

    @patch(f"{MODULE}.TrafficDailyReportGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    def test_executes_the_use_case_with_configured_layers_and_prefixed_filename(
        self,
        mock_source_repo,
        mock_daily_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """The use case must be built with configured layers, prefixed filename, and given output dir."""
        self._mock_configuration(mock_configuration, ["BORDE", "DINT"])
        use_case = MagicMock()
        use_case.execute.return_value = "/downloads/ScanBackup_2026-01-01.xlsx"
        mock_use_case_cls.return_value = use_case

        result = TrafficDailyReportGenerator.execute(
            date_str="2026-01-01", output_dir="/downloads"
        )

        mock_use_case_cls.assert_called_once_with(
            source_repository=mock_source_repo.return_value,
            daily_repository=mock_daily_repo.return_value,
            layers=["BORDE", "DINT"],
            data_date="2026-01-01",
            filename="ScanBackup_2026-01-01",
            output_dir=Path("/downloads"),
        )
        use_case.execute.assert_called_once()
        self.assertEqual(result, "/downloads/ScanBackup_2026-01-01.xlsx")

    @patch(f"{MODULE}.TrafficDailyReportGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    def test_no_output_dir_defaults_to_none(
        self,
        mock_source_repo,
        mock_daily_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """Omitting output_dir must pass None so the writer falls back to its default directory."""
        self._mock_configuration(mock_configuration, ["BORDE"])

        TrafficDailyReportGenerator.execute(date_str="2026-01-01")

        self.assertIsNone(
            mock_use_case_cls.call_args.kwargs["output_dir"]
        )

    @patch(f"{MODULE}.TrafficDailyReportGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    def test_no_date_str_defaults_to_yesterday(
        self,
        mock_source_repo,
        mock_daily_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """Omitting date_str must default to yesterday's date in ISO format."""
        self._mock_configuration(mock_configuration, ["BORDE"])
        expected_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        TrafficDailyReportGenerator.execute(date_str=None)

        self.assertEqual(
            mock_use_case_cls.call_args.kwargs["data_date"], expected_date
        )
        self.assertEqual(
            mock_use_case_cls.call_args.kwargs["filename"],
            f"ScanBackup_{expected_date}",
        )


class TestTrafficMonthlyReportGenerator(unittest.TestCase):
    """Unit tests for the TrafficMonthlyReportGenerator CLI orchestration class."""

    def _mock_configuration(self, mock_configuration, names: list[str]) -> MagicMock:
        """Wire a fake Configuration exposing the configured bbip layer names and report prefix."""
        layers = MagicMock()
        layers.bbip.names = names
        reports = MagicMock()
        reports.preffix_name = "ScanBackup"
        metadata = MagicMock()
        metadata.reports = reports
        config = mock_configuration.return_value
        config.get_cfg_layers.return_value = layers
        config.get_cfg_metadata.return_value = metadata
        return config

    @patch(f"{MODULE}.TrafficMonthlyReportGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    def test_executes_the_use_case_with_configured_layers_and_prefixed_filename(
        self,
        mock_source_repo,
        mock_daily_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """The use case must be built with configured layers, prefixed filename, and given output dir."""
        self._mock_configuration(mock_configuration, ["BORDE", "DINT"])
        use_case = MagicMock()
        use_case.execute.return_value = "/downloads/ScanBackup_2026-01.xlsx"
        mock_use_case_cls.return_value = use_case

        result = TrafficMonthlyReportGenerator.execute(
            month_str="2026-01", output_dir="/downloads"
        )

        mock_use_case_cls.assert_called_once_with(
            source_repository=mock_source_repo.return_value,
            daily_repository=mock_daily_repo.return_value,
            layers=["BORDE", "DINT"],
            year=2026,
            month=1,
            filename="ScanBackup_2026-01",
            output_dir=Path("/downloads"),
        )
        use_case.execute.assert_called_once()
        self.assertEqual(result, "/downloads/ScanBackup_2026-01.xlsx")

    @patch(f"{MODULE}.TrafficMonthlyReportGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    def test_no_output_dir_defaults_to_none(
        self,
        mock_source_repo,
        mock_daily_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """Omitting output_dir must pass None so the writer falls back to its default directory."""
        self._mock_configuration(mock_configuration, ["BORDE"])

        TrafficMonthlyReportGenerator.execute(month_str="2026-01")

        self.assertIsNone(mock_use_case_cls.call_args.kwargs["output_dir"])

    @patch(f"{MODULE}.TrafficMonthlyReportGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    def test_no_month_str_defaults_to_the_current_month(
        self,
        mock_source_repo,
        mock_daily_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """Omitting month_str must default to the current calendar month."""
        self._mock_configuration(mock_configuration, ["BORDE"])
        today = date.today()
        expected_year, expected_month = today.year, today.month

        TrafficMonthlyReportGenerator.execute(month_str=None)

        self.assertEqual(mock_use_case_cls.call_args.kwargs["year"], expected_year)
        self.assertEqual(mock_use_case_cls.call_args.kwargs["month"], expected_month)
        self.assertEqual(
            mock_use_case_cls.call_args.kwargs["filename"],
            f"ScanBackup_{expected_year:04d}-{expected_month:02d}",
        )


if __name__ == "__main__":
    unittest.main()
