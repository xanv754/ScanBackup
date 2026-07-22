import unittest
from unittest.mock import MagicMock
from scanbackup.application.use_case.database.inspect import DatabaseInspectUseCase


class TestDatabaseInspectUseCase(unittest.TestCase):
    """Unit tests for the DatabaseInspectUseCase."""

    def setUp(self) -> None:
        """Build a use case wired with a mocked database gateway."""
        self.database = MagicMock()
        self.use_case = DatabaseInspectUseCase(database=self.database)

    def test_execute_sets_the_uri_and_returns_the_collection_names(self) -> None:
        """execute() must configure the connection URI and return the listed collection names."""
        cfg_db = MagicMock()
        self.database.get_collection_names.return_value = ["TRAFFIC_SOURCE_BBIP"]

        result = self.use_case.execute(cfg_db=cfg_db)

        self.database.set_uri.assert_called_once_with(cfg_db)
        self.assertEqual(result, ["TRAFFIC_SOURCE_BBIP"])

    def test_propagates_errors_raised_by_the_database(self) -> None:
        """Any error raised by the database gateway must propagate unwrapped."""
        self.database.get_collection_names.side_effect = RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            self.use_case.execute(cfg_db=MagicMock())


if __name__ == "__main__":
    unittest.main()
