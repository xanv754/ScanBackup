import unittest
from unittest.mock import MagicMock, patch
from scanbackup.infrastructure.cli.database.inspect import get_collection_names

MODULE = "scanbackup.infrastructure.cli.database.inspect"


@patch(f"{MODULE}.Log")
class TestGetCollectionNames(unittest.TestCase):
    """Unit tests for the get_collection_names CLI orchestration function."""

    @patch(f"{MODULE}.Terminal")
    @patch(f"{MODULE}.DatabaseInspectUseCase")
    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_lists_the_database_collection_names(
        self, mock_configuration, mock_database_cls, mock_use_case_cls, mock_terminal_cls, mock_log
    ) -> None:
        """The collection names returned by the use case must be rendered as a list."""
        cfg_db = MagicMock()
        mock_configuration.return_value.get_cfg_database.return_value = cfg_db
        use_case = MagicMock()
        use_case.execute.return_value = ["TRAFFIC_SOURCE_BBIP"]
        mock_use_case_cls.return_value = use_case
        terminal = MagicMock()
        mock_terminal_cls.return_value = terminal

        get_collection_names()

        mock_use_case_cls.assert_called_once_with(database=mock_database_cls.return_value)
        use_case.execute.assert_called_once_with(cfg_db=cfg_db)
        terminal.list.assert_called_once_with(["TRAFFIC_SOURCE_BBIP"])

    @patch(f"{MODULE}.Terminal")
    @patch(f"{MODULE}.DatabaseInspectUseCase")
    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_exits_with_code_1_on_failure(
        self, mock_configuration, mock_database_cls, mock_use_case_cls, mock_terminal_cls, mock_log
    ) -> None:
        """Any failure while inspecting the database must terminate with exit(1)."""
        mock_use_case_cls.return_value.execute.side_effect = RuntimeError("boom")

        with self.assertRaises(SystemExit) as ctx:
            get_collection_names()
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
