import unittest
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.database.inspect import get_collection_names

MODULE = "scanbackup.application.cli.database.inspect"


@patch(f"{MODULE}.Log")
class TestGetCollectionNames(unittest.TestCase):
    """Unit tests for the get_collection_names CLI orchestration function."""

    @patch(f"{MODULE}.Terminal")
    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_lists_the_database_collection_names(
        self, mock_configuration, mock_database_cls, mock_terminal_cls, mock_log
    ) -> None:
        """The collection names returned by MongoDatabase must be rendered as a list."""
        database = MagicMock()
        database.get_collection_names.return_value = ["TRAFFIC_SOURCE_BBIP"]
        mock_database_cls.return_value = database
        terminal = MagicMock()
        mock_terminal_cls.return_value = terminal

        get_collection_names()

        terminal.list.assert_called_once_with(["TRAFFIC_SOURCE_BBIP"])

    @patch(f"{MODULE}.Terminal")
    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_exits_with_code_1_on_failure(
        self, mock_configuration, mock_database_cls, mock_terminal_cls, mock_log
    ) -> None:
        """Any failure while inspecting the database must terminate with exit(1)."""
        mock_database_cls.return_value.get_collection_names.side_effect = RuntimeError("boom")

        with self.assertRaises(SystemExit) as ctx:
            get_collection_names()
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
