import unittest
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.database.setup import setup_database

MODULE = "scanbackup.application.cli.database.setup"


@patch(f"{MODULE}.Terminal")
@patch(f"{MODULE}.Log")
class TestSetupDatabase(unittest.TestCase):
    """Unit tests for the setup_database CLI orchestration function."""

    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_creates_collections_using_configured_layers(
        self, mock_configuration, mock_database_cls, mock_log, mock_terminal
    ) -> None:
        """setup_database must wire the database with the config and create collections."""
        cfg_layers = MagicMock()
        mock_configuration.return_value.get_cfg_layers.return_value = cfg_layers
        database = MagicMock()
        mock_database_cls.return_value = database

        setup_database()

        database.create_collections.assert_called_once_with(config=cfg_layers)

    @patch(f"{MODULE}.MongoDatabase")
    @patch(f"{MODULE}.Configuration")
    def test_exits_with_code_1_on_failure(
        self, mock_configuration, mock_database_cls, mock_log, mock_terminal
    ) -> None:
        """Any failure during setup must terminate the process with exit(1)."""
        mock_database_cls.return_value.create_collections.side_effect = RuntimeError("boom")

        with self.assertRaises(SystemExit) as ctx:
            setup_database()
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
