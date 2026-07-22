import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from scanbackup.infrastructure.cli.summaries.updater import (
    TrafficSummaryUpdater,
    IPSummaryUpdater,
    TrafficHourSummaryUpdater,
    IPHourSummaryUpdater,
)

MODULE = "scanbackup.infrastructure.cli.summaries.updater"


class TestTrafficSummaryUpdater(unittest.TestCase):
    """Unit tests for the TrafficSummaryUpdater CLI orchestration class."""

    def _mock_configuration(self, mock_configuration, names: list[str]) -> None:
        """Wire a fake Configuration exposing the configured bbip layer names."""
        layers = MagicMock()
        layers.bbip.names = names
        mock_configuration.return_value.get_cfg_layers.return_value = layers

    @patch(f"{MODULE}.TrafficSummaryGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficHistoryBBIPRepository")
    def test_executes_the_use_case_with_configured_layers(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_daily_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """The use case must be built with every configured layer and the repositories, then executed."""
        self._mock_configuration(mock_configuration, ["BORDE", "DINT"])
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        TrafficSummaryUpdater.execute(date_str="2026-01-01")

        mock_use_case_cls.assert_called_once_with(
            source_repository=mock_source_repo.return_value,
            history_repository_factory=mock_history_repo_cls,
            daily_repository=mock_daily_repo.return_value,
            layers=["BORDE", "DINT"],
            data_date="2026-01-01",
        )
        use_case.execute.assert_called_once()

    @patch(f"{MODULE}.TrafficSummaryGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficHistoryBBIPRepository")
    def test_no_date_str_defaults_to_yesterday(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_daily_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """Omitting date_str must default to yesterday's date in ISO format."""
        self._mock_configuration(mock_configuration, ["BORDE"])
        expected_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        TrafficSummaryUpdater.execute(date_str=None)

        self.assertEqual(
            mock_use_case_cls.call_args.kwargs["data_date"], expected_date
        )


class TestIPSummaryUpdater(unittest.TestCase):
    """Unit tests for the IPSummaryUpdater CLI orchestration class."""

    def _mock_configuration(self, mock_configuration, names: list[str]) -> None:
        """Wire a fake Configuration exposing the configured ip layer names."""
        layers = MagicMock()
        layers.ip.names = names
        mock_configuration.return_value.get_cfg_layers.return_value = layers

    @patch(f"{MODULE}.IPSummaryGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoIPDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoIPSourceBBIPRepository")
    @patch(f"{MODULE}.MongoIPHistoryBBIPRepository")
    def test_executes_the_use_case_with_configured_layers(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_daily_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """The use case must be built with every configured layer and the repositories, then executed."""
        self._mock_configuration(mock_configuration, ["IP_BRAS"])
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        IPSummaryUpdater.execute(date_str="2026-01-01")

        mock_use_case_cls.assert_called_once_with(
            source_repository=mock_source_repo.return_value,
            history_repository_factory=mock_history_repo_cls,
            daily_repository=mock_daily_repo.return_value,
            layers=["IP_BRAS"],
            data_date="2026-01-01",
        )
        use_case.execute.assert_called_once()

    @patch(f"{MODULE}.IPSummaryGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoIPDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoIPSourceBBIPRepository")
    @patch(f"{MODULE}.MongoIPHistoryBBIPRepository")
    def test_no_date_str_defaults_to_yesterday(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_daily_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """Omitting date_str must default to yesterday's date in ISO format."""
        self._mock_configuration(mock_configuration, ["IP_BRAS"])
        expected_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        IPSummaryUpdater.execute(date_str=None)

        self.assertEqual(
            mock_use_case_cls.call_args.kwargs["data_date"], expected_date
        )


class TestTrafficHourSummaryUpdater(unittest.TestCase):
    """Unit tests for the TrafficHourSummaryUpdater CLI orchestration class."""

    def _mock_configuration(self, mock_configuration, names: list[str]) -> None:
        """Wire a fake Configuration exposing the configured bbip layer names."""
        layers = MagicMock()
        layers.bbip.names = names
        mock_configuration.return_value.get_cfg_layers.return_value = layers

    @patch(f"{MODULE}.TrafficHourSummaryGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficHourSummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficHistoryBBIPRepository")
    def test_executes_the_use_case_with_configured_layers(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_hour_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """The use case must be built with every configured layer and the repositories, then executed."""
        self._mock_configuration(mock_configuration, ["BORDE", "DINT"])
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        TrafficHourSummaryUpdater.execute(date_str="2026-01-01")

        mock_use_case_cls.assert_called_once_with(
            source_repository=mock_source_repo.return_value,
            history_repository_factory=mock_history_repo_cls,
            hour_repository=mock_hour_repo.return_value,
            layers=["BORDE", "DINT"],
            data_date="2026-01-01",
        )
        use_case.execute.assert_called_once()

    @patch(f"{MODULE}.TrafficHourSummaryGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficHourSummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficHistoryBBIPRepository")
    def test_no_date_str_defaults_to_yesterday(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_hour_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """Omitting date_str must default to yesterday's date in ISO format."""
        self._mock_configuration(mock_configuration, ["BORDE"])
        expected_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        TrafficHourSummaryUpdater.execute(date_str=None)

        self.assertEqual(
            mock_use_case_cls.call_args.kwargs["data_date"], expected_date
        )


class TestIPHourSummaryUpdater(unittest.TestCase):
    """Unit tests for the IPHourSummaryUpdater CLI orchestration class."""

    def _mock_configuration(self, mock_configuration, names: list[str]) -> None:
        """Wire a fake Configuration exposing the configured ip layer names."""
        layers = MagicMock()
        layers.ip.names = names
        mock_configuration.return_value.get_cfg_layers.return_value = layers

    @patch(f"{MODULE}.IPHourSummaryGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoIPHourSummaryBBIPRepository")
    @patch(f"{MODULE}.MongoIPSourceBBIPRepository")
    @patch(f"{MODULE}.MongoIPHistoryBBIPRepository")
    def test_executes_the_use_case_with_configured_layers(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_hour_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """The use case must be built with every configured layer and the repositories, then executed."""
        self._mock_configuration(mock_configuration, ["IP_BRAS"])
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        IPHourSummaryUpdater.execute(date_str="2026-01-01")

        mock_use_case_cls.assert_called_once_with(
            source_repository=mock_source_repo.return_value,
            history_repository_factory=mock_history_repo_cls,
            hour_repository=mock_hour_repo.return_value,
            layers=["IP_BRAS"],
            data_date="2026-01-01",
        )
        use_case.execute.assert_called_once()

    @patch(f"{MODULE}.IPHourSummaryGeneratorUseCase")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoIPHourSummaryBBIPRepository")
    @patch(f"{MODULE}.MongoIPSourceBBIPRepository")
    @patch(f"{MODULE}.MongoIPHistoryBBIPRepository")
    def test_no_date_str_defaults_to_yesterday(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_hour_repo,
        mock_configuration,
        mock_use_case_cls,
    ) -> None:
        """Omitting date_str must default to yesterday's date in ISO format."""
        self._mock_configuration(mock_configuration, ["IP_BRAS"])
        expected_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        IPHourSummaryUpdater.execute(date_str=None)

        self.assertEqual(
            mock_use_case_cls.call_args.kwargs["data_date"], expected_date
        )


if __name__ == "__main__":
    unittest.main()
