from pathlib import Path
from unittest.mock import MagicMock, patch
from scanbackup.shared.outputs.logs import LogHandler
from tests.support import TempDirTestCase


class TestLogHandler(TempDirTestCase):
    """Unit tests for the LogHandler class, isolated from the real log file."""

    def _mock_configuration(self, base_dir: Path) -> MagicMock:
        """Build a fake Configuration pointing logs to a temporary directory."""
        log_cfg = MagicMock()
        log_cfg.dir_name = "logs"
        log_cfg.filename = "scanbackup_test"
        log_cfg.extension = "log"
        log_cfg.msg_format = "%(asctime)s %(levelname)s %(message)s"
        log_cfg.date_format = "%Y-%m-%d %H:%M:%S"

        metadata = MagicMock()
        metadata.dir_data = str(base_dir)
        metadata.logs = log_cfg

        config = MagicMock()
        config.get_cfg_metadata.return_value = metadata
        return config

    @patch("scanbackup.shared.outputs.logs.Path")
    @patch("scanbackup.shared.outputs.logs.Configuration")
    def test_creates_log_file_under_configured_directory(
        self, mock_configuration, mock_path_cls
    ) -> None:
        """A successful initialization must create the log directory and file."""
        mock_configuration.return_value = self._mock_configuration(self.tmp_dir)
        # LogHandler builds the filepath as Path(__file__).parent*4 / dir_data / dir_name / filename
        # so instead of reassembling that chain, we point Path(...) construction at a
        # real temporary path by letting the real Path class do the work.
        mock_path_cls.side_effect = Path

        handler = LogHandler()

        log_file = Path(handler.filepath)
        self.assertTrue(log_file.exists())
        self.assertTrue(log_file.name.startswith("scanbackup_test"))
        handler.file_handler.close()

    @patch("scanbackup.shared.outputs.logs.exit", create=True)
    @patch("scanbackup.shared.outputs.logs.Configuration")
    def test_exits_on_initialization_failure(self, mock_configuration, mock_exit) -> None:
        """A failure while reading configuration must exit the process with code 1."""
        mock_configuration.side_effect = RuntimeError("config unavailable")

        LogHandler()

        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    import unittest

    unittest.main()
