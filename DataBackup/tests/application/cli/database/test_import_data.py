import unittest
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.database.import_data import import_data_to_database

MODULE = "scanbackup.application.cli.database.import_data"


@patch(f"{MODULE}.Terminal")
@patch(f"{MODULE}.Log")
class TestImportDataToDatabase(unittest.TestCase):
    """Unit tests for the import_data_to_database CLI orchestration function."""

    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_delegates_to_mongo_database_import_data(
        self, mock_configuration, mock_database_cls, mock_log, mock_terminal
    ) -> None:
        """import_data_to_database must forward the collection/filepath/delimiter."""
        cfg_layers = MagicMock()
        mock_configuration.return_value.get_cfg_layers.return_value = cfg_layers
        database = MagicMock()
        mock_database_cls.return_value = database

        import_data_to_database(
            collection="TRAFFIC_SOURCE_BBIP", filepath="/tmp/in.csv", delimiter=";"
        )

        database.import_data.assert_called_once_with(
            name_collection="TRAFFIC_SOURCE_BBIP",
            config=cfg_layers,
            input_filepath="/tmp/in.csv",
            delimiter=";",
        )

    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_exits_with_code_1_on_failure(
        self, mock_configuration, mock_database_cls, mock_log, mock_terminal
    ) -> None:
        """Any failure during import must terminate the process with exit(1)."""
        mock_database_cls.return_value.import_data.side_effect = RuntimeError("boom")

        with self.assertRaises(SystemExit) as ctx:
            import_data_to_database(
                collection="TRAFFIC_SOURCE_BBIP", filepath="/tmp/in.csv", delimiter=";"
            )
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
