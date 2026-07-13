import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.history.updater import (
    TrafficHistoryUpdater,
    IPHistoryUpdater,
)

MODULE = "scanbackup.application.cli.history.updater"


class TestTrafficHistoryUpdater(unittest.TestCase):
    """Unit tests for the TrafficHistoryUpdater CLI orchestration class."""

    def _mock_configuration(self, mock_configuration) -> MagicMock:
        """Wire a fake Configuration exposing the scanner credentials and max_workers."""
        scanner = MagicMock()
        scanner.scan_credentials.username = " user "
        scanner.scan_credentials.password = " pass "
        scanner.max_workers = 5
        metadata = MagicMock()
        metadata.scanner = scanner
        mock_configuration.return_value.get_cfg_metadata.return_value = metadata
        return scanner

    @patch(f"{MODULE}.TrafficCollectorUseCase")
    @patch(f"{MODULE}.MRTGFetcher")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficHistoryBBIPRepository")
    def test_executes_the_use_case_with_every_active_source(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_configuration,
        mock_fetcher_cls,
        mock_use_case_cls,
    ) -> None:
        """The use case must be built with the fetcher, factory and repositories, then executed."""
        scanner = self._mock_configuration(mock_configuration)
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        TrafficHistoryUpdater.execute(date_str="2026-01-01")

        mock_fetcher_cls.assert_called_once_with(username="user", password="pass")
        mock_use_case_cls.assert_called_once_with(
            source_repository=mock_source_repo.return_value,
            history_repository_factory=mock_history_repo_cls,
            fetcher=mock_fetcher_cls.return_value,
            data_date="2026-01-01",
            max_workers=scanner.max_workers,
        )
        use_case.execute.assert_called_once()

    @patch(f"{MODULE}.TrafficCollectorUseCase")
    @patch(f"{MODULE}.MRTGFetcher")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficHistoryBBIPRepository")
    def test_no_date_str_defaults_to_yesterday(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_configuration,
        mock_fetcher_cls,
        mock_use_case_cls,
    ) -> None:
        """Omitting date_str must default to yesterday's date in ISO format."""
        self._mock_configuration(mock_configuration)
        expected_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        TrafficHistoryUpdater.execute(date_str=None)

        self.assertEqual(
            mock_use_case_cls.call_args.kwargs["data_date"], expected_date
        )


class TestIPHistoryUpdater(unittest.TestCase):
    """Unit tests for the IPHistoryUpdater CLI orchestration class."""

    def _mock_configuration(self, mock_configuration) -> MagicMock:
        """Wire a fake Configuration exposing the scanner credentials and max_workers."""
        scanner = MagicMock()
        scanner.scan_credentials.username = " user "
        scanner.scan_credentials.password = " pass "
        scanner.max_workers = 5
        metadata = MagicMock()
        metadata.scanner = scanner
        mock_configuration.return_value.get_cfg_metadata.return_value = metadata
        return scanner

    @patch(f"{MODULE}.IPCollectorUseCase")
    @patch(f"{MODULE}.IPActiveFetcher")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoIPSourceBBIPRepository")
    @patch(f"{MODULE}.MongoIPHistoryBBIPRepository")
    def test_executes_the_use_case_with_every_active_source(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_configuration,
        mock_fetcher_cls,
        mock_use_case_cls,
    ) -> None:
        """The use case must be built with the fetcher, factory and repositories, then executed."""
        scanner = self._mock_configuration(mock_configuration)
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        IPHistoryUpdater.execute(date_str="2026-01-01")

        mock_fetcher_cls.assert_called_once_with(username="user", password="pass")
        mock_use_case_cls.assert_called_once_with(
            source_repository=mock_source_repo.return_value,
            history_repository_factory=mock_history_repo_cls,
            fetcher=mock_fetcher_cls.return_value,
            data_date="2026-01-01",
            max_workers=scanner.max_workers,
        )
        use_case.execute.assert_called_once()

    @patch(f"{MODULE}.IPCollectorUseCase")
    @patch(f"{MODULE}.IPActiveFetcher")
    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoIPSourceBBIPRepository")
    @patch(f"{MODULE}.MongoIPHistoryBBIPRepository")
    def test_no_date_str_defaults_to_yesterday(
        self,
        mock_history_repo_cls,
        mock_source_repo,
        mock_configuration,
        mock_fetcher_cls,
        mock_use_case_cls,
    ) -> None:
        """Omitting date_str must default to yesterday's date in ISO format."""
        self._mock_configuration(mock_configuration)
        expected_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        IPHistoryUpdater.execute(date_str=None)

        self.assertEqual(
            mock_use_case_cls.call_args.kwargs["data_date"], expected_date
        )


if __name__ == "__main__":
    unittest.main()
