import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.history.updater import TrafficHistoryUpdater
from scanbackup.shared import LayerNotDefined

MODULE = "scanbackup.application.cli.history.updater"


class TestTrafficHistoryUpdater(unittest.TestCase):
    """Unit tests for the TrafficHistoryUpdater CLI orchestration class."""

    @patch(f"{MODULE}.TrafficHistoryUpdaterUseCase")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficHistoryBBIPRepository")
    @patch(f"{MODULE}.ValidatorConfig")
    def test_executes_the_use_case_for_a_valid_bbip_layer(
        self,
        mock_validator,
        mock_history_repo,
        mock_source_repo,
        mock_daily_repo,
        mock_use_case_cls,
    ) -> None:
        """A layer accepted as a BBIP layer must build and execute the use case."""
        mock_validator.valid_layer_bbip.return_value = True
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        TrafficHistoryUpdater.execute(layer="borde", date_str="2026-01-01")

        mock_use_case_cls.assert_called_once_with(
            layer="BORDE",
            history_repository=mock_history_repo.return_value,
            source_repository=mock_source_repo.return_value,
            daily_repository=mock_daily_repo.return_value,
            data_date="2026-01-01",
        )
        use_case.execute.assert_called_once()

    @patch(f"{MODULE}.TrafficHistoryUpdaterUseCase")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficHistoryBBIPRepository")
    @patch(f"{MODULE}.ValidatorConfig")
    def test_layer_invalid_as_bbip_but_valid_as_ip_raises(
        self,
        mock_validator,
        mock_history_repo,
        mock_source_repo,
        mock_daily_repo,
        mock_use_case_cls,
    ) -> None:
        """A layer only valid as an IP layer must be rejected for this BBIP endpoint."""
        mock_validator.valid_layer_bbip.return_value = False
        mock_validator.valid_layer_ip.return_value = True

        with self.assertRaises(LayerNotDefined):
            TrafficHistoryUpdater.execute(layer="dint", date_str="2026-01-01")
        mock_use_case_cls.assert_not_called()

    @patch(f"{MODULE}.TrafficHistoryUpdaterUseCase")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficHistoryBBIPRepository")
    @patch(f"{MODULE}.ValidatorConfig")
    def test_layer_invalid_in_both_systems_raises(
        self,
        mock_validator,
        mock_history_repo,
        mock_source_repo,
        mock_daily_repo,
        mock_use_case_cls,
    ) -> None:
        """A layer unknown to both BBIP and IP configs must still be rejected."""
        mock_validator.valid_layer_bbip.return_value = False
        mock_validator.valid_layer_ip.return_value = False

        with self.assertRaises(LayerNotDefined):
            TrafficHistoryUpdater.execute(layer="unknown", date_str="2026-01-01")
        mock_use_case_cls.assert_not_called()

    @patch(f"{MODULE}.TrafficHistoryUpdaterUseCase")
    @patch(f"{MODULE}.MongoTrafficDailySummaryBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.MongoTrafficHistoryBBIPRepository")
    @patch(f"{MODULE}.ValidatorConfig")
    def test_no_date_str_defaults_to_yesterday(
        self,
        mock_validator,
        mock_history_repo,
        mock_source_repo,
        mock_daily_repo,
        mock_use_case_cls,
    ) -> None:
        """Omitting date_str must default to yesterday's date in ISO format."""
        mock_validator.valid_layer_bbip.return_value = True
        expected_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        TrafficHistoryUpdater.execute(layer="borde", date_str=None)

        self.assertEqual(
            mock_use_case_cls.call_args.kwargs["data_date"], expected_date
        )


if __name__ == "__main__":
    unittest.main()
