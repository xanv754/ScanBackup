import unittest
from unittest.mock import patch
from click.testing import CliRunner
from scanbackup.infrastructure.cli.database.main import cli

MODULE = "scanbackup.infrastructure.cli.database.main"


class TestDatabaseCli(unittest.TestCase):
    """Unit tests for the database CLI command wiring."""

    def setUp(self) -> None:
        """Build a Click test runner shared across assertions."""
        self.runner = CliRunner()

    @patch(f"{MODULE}.setup_database")
    def test_setup_delegates_to_setup_database(self, mock_setup) -> None:
        """The 'setup' command must call setup_database() with no arguments."""
        result = self.runner.invoke(cli, ["setup"])
        self.assertEqual(result.exit_code, 0)
        mock_setup.assert_called_once_with()

    @patch(f"{MODULE}.get_collection_names")
    def test_inspect_delegates_to_get_collection_names(self, mock_inspect) -> None:
        """The 'inspect' command must call get_collection_names() with no arguments."""
        result = self.runner.invoke(cli, ["inspect"])
        self.assertEqual(result.exit_code, 0)
        mock_inspect.assert_called_once_with()

    @patch(f"{MODULE}.import_data_to_database")
    def test_import_delegates_with_given_options(self, mock_import) -> None:
        """The 'import' command must forward collection/filepath/delimiter."""
        with self.runner.isolated_filesystem():
            with open("data.csv", "w") as f:
                f.write("a;b\n1;2\n")
            result = self.runner.invoke(
                cli,
                [
                    "import",
                    "--collection",
                    "TRAFFIC_SOURCE_BBIP",
                    "--filepath",
                    "data.csv",
                    "--delimiter",
                    ";",
                ],
            )
        self.assertEqual(result.exit_code, 0)
        mock_import.assert_called_once_with(
            collection="TRAFFIC_SOURCE_BBIP", filepath="data.csv", delimiter=";"
        )

    @patch(f"{MODULE}.export_data_from_database")
    def test_export_delegates_with_given_options(self, mock_export) -> None:
        """The 'export' command must forward collection/dirpath/delimiter/id."""
        with self.runner.isolated_filesystem():
            import os

            os.mkdir("out")
            result = self.runner.invoke(
                cli,
                [
                    "export",
                    "--collection",
                    "TRAFFIC_SOURCE_BBIP",
                    "--dirpath",
                    "out",
                    "--id",
                ],
            )
        self.assertEqual(result.exit_code, 0)
        mock_export.assert_called_once_with(
            collection="TRAFFIC_SOURCE_BBIP", dirpath="out", delimiter=None, id=True
        )


if __name__ == "__main__":
    unittest.main()
