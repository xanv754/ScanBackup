import unittest
from pathlib import Path
from unittest.mock import MagicMock
from scanbackup.application.use_case.database.export_data import DatabaseExportUseCase


class TestDatabaseExportUseCase(unittest.TestCase):
    """Unit tests for the DatabaseExportUseCase."""

    def setUp(self) -> None:
        """Build a use case wired with a mocked database gateway."""
        self.database = MagicMock()
        self.use_case = DatabaseExportUseCase(database=self.database)

    def test_execute_sets_the_uri_and_returns_the_exported_filepath(self) -> None:
        """execute() must configure the connection URI, forward every argument, and return the filepath."""
        cfg_db = MagicMock()
        cfg_layers = MagicMock()
        self.database.export_data.return_value = "/tmp/out.csv"

        result = self.use_case.execute(
            cfg_db=cfg_db,
            cfg_layers=cfg_layers,
            name_collection="TRAFFIC_SOURCE_BBIP",
            dirpath=Path("/tmp"),
            include_id=True,
        )

        self.database.set_uri.assert_called_once_with(cfg_db)
        self.database.export_data.assert_called_once_with(
            config=cfg_layers,
            name_collection="TRAFFIC_SOURCE_BBIP",
            dirpath=Path("/tmp"),
            include_id=True,
        )
        self.assertEqual(result, "/tmp/out.csv")

    def test_propagates_errors_raised_by_the_database(self) -> None:
        """Any error raised by the database gateway must propagate unwrapped."""
        self.database.export_data.side_effect = RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            self.use_case.execute(
                cfg_db=MagicMock(),
                cfg_layers=MagicMock(),
                name_collection="TRAFFIC_SOURCE_BBIP",
                dirpath=Path("/tmp"),
                include_id=False,
            )


if __name__ == "__main__":
    unittest.main()
