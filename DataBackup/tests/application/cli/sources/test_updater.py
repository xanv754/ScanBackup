import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.sources.updater import scrapper_sources

MODULE = "scanbackup.application.cli.sources.updater"


class TestScrapperSources(unittest.TestCase):
    """Unit tests for the scrapper_sources CLI orchestration function."""

    @patch(f"{MODULE}.UpdaterSources")
    def test_executes_with_default_layer_and_no_outdir(self, mock_updater_cls) -> None:
        """With defaults, execute() must be called with layer='all' and outpath=None."""
        updater = MagicMock()
        mock_updater_cls.return_value = updater

        scrapper_sources()

        updater.execute.assert_called_once_with(layer="all", outpath=None)

    @patch(f"{MODULE}.UpdaterSources")
    def test_executes_with_given_layer_and_outdir(self, mock_updater_cls) -> None:
        """A given layer and outdir must be forwarded as layer/outpath."""
        updater = MagicMock()
        mock_updater_cls.return_value = updater
        outdir = Path("/tmp/out")

        scrapper_sources(layer="BORDE", outdir=outdir)

        updater.execute.assert_called_once_with(layer="BORDE", outpath=outdir)


if __name__ == "__main__":
    unittest.main()
