import unittest
from unittest.mock import MagicMock, patch
from scanbackup.infrastructure.cli.database.import_data import import_data_to_database

MODULE = "scanbackup.infrastructure.cli.database.import_data"


@patch(f"{MODULE}.Terminal")
@patch(f"{MODULE}.Log")
class TestImportDataToDatabase(unittest.TestCase):
    """Unit tests for the import_data_to_database CLI orchestration function."""

    @patch(f"{MODULE}.DatabaseImportUseCase")
    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_executes_the_use_case_with_the_collection_filepath_and_delimiter(
        self, mock_configuration, mock_database_cls, mock_use_case_cls, mock_log, mock_terminal
    ) -> None:
        """import_data_to_database must build the use case and execute it with the given options."""
        cfg_db = MagicMock()
        cfg_layers = MagicMock()
        mock_configuration.return_value.get_cfg_database.return_value = cfg_db
        mock_configuration.return_value.get_cfg_layers.return_value = cfg_layers
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        import_data_to_database(
            collection="TRAFFIC_SOURCE_BBIP", filepath="/tmp/in.csv", delimiter=";"
        )

        mock_use_case_cls.assert_called_once_with(database=mock_database_cls.return_value)
        use_case.execute.assert_called_once_with(
            cfg_db=cfg_db,
            cfg_layers=cfg_layers,
            name_collection="TRAFFIC_SOURCE_BBIP",
            input_filepath="/tmp/in.csv",
            delimiter=";",
        )

    @patch(f"{MODULE}.DatabaseImportUseCase")
    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_exits_with_code_1_on_failure(
        self, mock_configuration, mock_database_cls, mock_use_case_cls, mock_log, mock_terminal
    ) -> None:
        """Any failure during import must terminate the process with exit(1)."""
        mock_use_case_cls.return_value.execute.side_effect = RuntimeError("boom")

        with self.assertRaises(SystemExit) as ctx:
            import_data_to_database(
                collection="TRAFFIC_SOURCE_BBIP", filepath="/tmp/in.csv", delimiter=";"
            )
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
