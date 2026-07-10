import unittest
from unittest.mock import patch
from pathlib import Path
from click.testing import CliRunner
from scanbackup.application.cli.sources.main import cli

MODULE = "scanbackup.application.cli.sources.main"


class TestSourcesCli(unittest.TestCase):
    """Unit tests for the sources CLI command wiring."""

    def setUp(self) -> None:
        """Build a Click test runner shared across assertions."""
        self.runner = CliRunner()

    @patch(f"{MODULE}.traffic_upload_to_database")
    def test_traffic_upload_delegates_with_given_filepath(self, mock_upload) -> None:
        """The 'traffic-upload' command must forward --filepath as file=."""
        with self.runner.isolated_filesystem():
            with open("sources.csv", "w") as f:
                f.write("link;enlace\n")
            result = self.runner.invoke(
                cli, ["traffic-upload", "--filepath", "sources.csv"]
            )
        self.assertEqual(result.exit_code, 0)
        mock_upload.assert_called_once_with(file="sources.csv")

    @patch(f"{MODULE}.traffic_export_from_database")
    def test_traffic_export_delegates_with_given_options(self, mock_export) -> None:
        """The 'traffic-export' command must forward --dirpath and --layer."""
        with self.runner.isolated_filesystem():
            import os

            os.mkdir("out")
            result = self.runner.invoke(
                cli, ["traffic-export", "--dirpath", "out", "--layer", "BORDE"]
            )
        self.assertEqual(result.exit_code, 0)
        mock_export.assert_called_once_with(path="out", layer="BORDE")

    @patch(f"{MODULE}.scrapper_sources")
    def test_updater_without_outdir_uses_default_signature(self, mock_scrapper) -> None:
        """The 'updater' command without --outdir must call scrapper_sources(layer=...)."""
        result = self.runner.invoke(cli, ["updater", "--layer", "all"])
        self.assertEqual(result.exit_code, 0)
        mock_scrapper.assert_called_once_with(layer="all")

    @patch(f"{MODULE}.scrapper_sources")
    def test_updater_with_outdir_passes_a_path(self, mock_scrapper) -> None:
        """The 'updater' command with --outdir must call scrapper_sources with a Path."""
        with self.runner.isolated_filesystem():
            import os

            os.mkdir("out")
            result = self.runner.invoke(
                cli, ["updater", "--layer", "all", "--outdir", "out"]
            )
        self.assertEqual(result.exit_code, 0)
        mock_scrapper.assert_called_once_with(layer="all", outdir=Path("out"))


if __name__ == "__main__":
    unittest.main()
