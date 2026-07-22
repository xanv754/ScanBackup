import unittest
from unittest.mock import MagicMock
from scanbackup.application.use_case.database.import_data import DatabaseImportUseCase


class TestDatabaseImportUseCase(unittest.TestCase):
    """Unit tests for the DatabaseImportUseCase."""

    def setUp(self) -> None:
        """Build a use case wired with a mocked database gateway."""
        self.database = MagicMock()
        self.use_case = DatabaseImportUseCase(database=self.database)

    def test_execute_sets_the_uri_and_delegates_to_the_database(self) -> None:
        """execute() must configure the connection URI and forward every argument."""
        cfg_db = MagicMock()
        cfg_layers = MagicMock()

        self.use_case.execute(
            cfg_db=cfg_db,
            cfg_layers=cfg_layers,
            name_collection="TRAFFIC_SOURCE_BBIP",
            input_filepath="/tmp/in.csv",
            delimiter=";",
        )

        self.database.set_uri.assert_called_once_with(cfg_db)
        self.database.import_data.assert_called_once_with(
            name_collection="TRAFFIC_SOURCE_BBIP",
            config=cfg_layers,
            input_filepath="/tmp/in.csv",
            delimiter=";",
        )

    def test_propagates_errors_raised_by_the_database(self) -> None:
        """Any error raised by the database gateway must propagate unwrapped."""
        self.database.import_data.side_effect = RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            self.use_case.execute(
                cfg_db=MagicMock(),
                cfg_layers=MagicMock(),
                name_collection="TRAFFIC_SOURCE_BBIP",
                input_filepath="/tmp/in.csv",
                delimiter=";",
            )


if __name__ == "__main__":
    unittest.main()
