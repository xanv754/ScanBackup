import unittest
from click.testing import CliRunner
from scanbackup.application.cli.main import cli


class TestSystemCli(unittest.TestCase):
    """Unit tests for the top-level scanbackup CLI wiring."""

    def setUp(self) -> None:
        """Build a Click test runner shared across assertions."""
        self.runner = CliRunner()

    def test_registers_all_subcommands(self) -> None:
        """The root group must expose database, scanner, sources and history."""
        result = self.runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        for name in ["database", "scanner", "sources", "history"]:
            self.assertIn(name, result.output)


if __name__ == "__main__":
    unittest.main()
