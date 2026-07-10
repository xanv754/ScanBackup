import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.sources.upload_db import traffic_upload_to_database

MODULE = "scanbackup.application.cli.sources.upload_db"


@patch(f"{MODULE}.Terminal")
@patch(f"{MODULE}.Log")
class TestTrafficUploadToDatabase(unittest.TestCase):
    """Unit tests for the traffic_upload_to_database CLI orchestration function."""

    @patch(f"{MODULE}.TrafficSourceUpdaterUseCase")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    def test_executes_the_use_case_with_the_given_file(
        self, mock_repo_cls, mock_use_case_cls, mock_log, mock_terminal
    ) -> None:
        """The given filepath must be wrapped into a Path and passed to the use case."""
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        traffic_upload_to_database("/tmp/sources.csv")

        mock_use_case_cls.assert_called_once_with(
            repository=mock_repo_cls.return_value, path=Path("/tmp/sources.csv")
        )
        use_case.execute.assert_called_once()

    @patch(f"{MODULE}.TrafficSourceUpdaterUseCase")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    def test_failure_is_logged_without_raising(
        self, mock_repo_cls, mock_use_case_cls, mock_log, mock_terminal
    ) -> None:
        """A failure during the use case execution must be reported, not raised."""
        mock_use_case_cls.return_value.execute.side_effect = RuntimeError("boom")

        traffic_upload_to_database("/tmp/sources.csv")


if __name__ == "__main__":
    unittest.main()
