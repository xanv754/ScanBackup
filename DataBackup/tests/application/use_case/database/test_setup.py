import unittest
from unittest.mock import MagicMock
from scanbackup.application.use_case.database.setup import DatabaseSetupUseCase


class TestDatabaseSetupUseCase(unittest.TestCase):
    """Unit tests for the DatabaseSetupUseCase."""

    def setUp(self) -> None:
        """Build a use case wired with a mocked database gateway."""
        self.database = MagicMock()
        self.use_case = DatabaseSetupUseCase(database=self.database)

    def test_execute_sets_the_uri_before_creating_collections(self) -> None:
        """execute() must configure the connection URI before creating collections."""
        cfg_db = MagicMock()
        cfg_layers = MagicMock()

        self.use_case.execute(cfg_db=cfg_db, cfg_layers=cfg_layers)

        self.database.set_uri.assert_called_once_with(cfg_db)
        self.database.create_collections.assert_called_once_with(config=cfg_layers)

    def test_propagates_errors_raised_by_the_database(self) -> None:
        """Any error raised by the database gateway must propagate unwrapped."""
        self.database.create_collections.side_effect = RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            self.use_case.execute(cfg_db=MagicMock(), cfg_layers=MagicMock())


if __name__ == "__main__":
    unittest.main()
