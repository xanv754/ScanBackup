import unittest
from unittest.mock import patch
from click.testing import CliRunner
from scanbackup.application.cli.collector.main import cli

MODULE = "scanbackup.application.cli.collector.main"


class TestCollectorCli(unittest.TestCase):
    """Unit tests for the collector CLI command wiring."""

    def setUp(self) -> None:
        """Build a Click test runner shared across assertions."""
        self.runner = CliRunner()

    @patch(f"{MODULE}.recolector")
    def test_run_delegates_to_recolector_with_given_options(self, mock_recolector) -> None:
        """The 'run' command must forward --date and --layer to recolector()."""
        result = self.runner.invoke(
            cli, ["run", "--date", "2026-01-01", "--layer", "BORDE"]
        )
        self.assertEqual(result.exit_code, 0)
        mock_recolector.assert_called_once_with(date="2026-01-01", layer="BORDE")

    @patch(f"{MODULE}.recolector")
    def test_run_without_options_uses_defaults(self, mock_recolector) -> None:
        """The 'run' command must call recolector() with None when no option is given."""
        result = self.runner.invoke(cli, ["run"])
        self.assertEqual(result.exit_code, 0)
        mock_recolector.assert_called_once_with(date=None, layer=None)


if __name__ == "__main__":
    unittest.main()
