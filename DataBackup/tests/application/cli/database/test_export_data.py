import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.database.export_data import export_data_from_database

MODULE = "scanbackup.application.cli.database.export_data"


@patch(f"{MODULE}.Log")
class TestExportDataFromDatabase(unittest.TestCase):
    """Unit tests for the export_data_from_database CLI orchestration function."""

    @patch(f"{MODULE}.Terminal")
    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_reports_the_exported_filepath(
        self, mock_configuration, mock_database_cls, mock_terminal_cls, mock_log
    ) -> None:
        """The final message must include the filepath returned by export_data."""
        cfg_layers = MagicMock()
        mock_configuration.return_value.get_cfg_layers.return_value = cfg_layers
        database = MagicMock()
        database.export_data.return_value = "/tmp/out.csv"
        mock_database_cls.return_value = database
        terminal = MagicMock()
        mock_terminal_cls.return_value = terminal

        export_data_from_database(collection="TRAFFIC_SOURCE_BBIP", dirpath="/tmp")

        database.export_data.assert_called_once_with(
            config=cfg_layers,
            name_collection="TRAFFIC_SOURCE_BBIP",
            dirpath=Path("/tmp"),
            include_id=False,
        )
        final_message = terminal.info.call_args_list[-1].args[0]
        self.assertIn("/tmp/out.csv", final_message)

    @patch(f"{MODULE}.Terminal")
    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_exits_with_code_1_on_failure(
        self, mock_configuration, mock_database_cls, mock_terminal_cls, mock_log
    ) -> None:
        """Any failure during export must terminate the process with exit(1)."""
        mock_database_cls.return_value.export_data.side_effect = RuntimeError("boom")

        with self.assertRaises(SystemExit) as ctx:
            export_data_from_database(collection="TRAFFIC_SOURCE_BBIP", dirpath="/tmp")
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
