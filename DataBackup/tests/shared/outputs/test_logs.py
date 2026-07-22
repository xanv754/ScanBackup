import logging
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

    @patch("scanbackup.shared.outputs.logs.TimedRotatingFileHandler")
    @patch("scanbackup.shared.outputs.logs.logging.Formatter")
    @patch("scanbackup.shared.outputs.logs.Configuration")
    def test_builds_formatter_from_configured_formats(
        self, mock_configuration, mock_formatter_cls, mock_handler_cls
    ) -> None:
        """The Formatter must use the msg_format/date_format from configuration, not hardcoded strings."""
        config = self._mock_configuration(self.tmp_dir)
        mock_configuration.return_value = config
        mock_handler_cls.return_value = MagicMock()

        LogHandler()

        log_cfg = config.get_cfg_metadata().logs
        mock_formatter_cls.assert_called_once_with(log_cfg.msg_format, log_cfg.date_format)

    @patch("scanbackup.shared.outputs.logs.TimedRotatingFileHandler")
    @patch("scanbackup.shared.outputs.logs.logging.Formatter")
    @patch("scanbackup.shared.outputs.logs.Configuration")
    def test_creates_rotating_handler_with_expected_parameters(
        self, mock_configuration, mock_formatter_cls, mock_handler_cls
    ) -> None:
        """The rotating handler must roll weekly, keep 4 backups, use utf-8 and UTC timestamps."""
        config = self._mock_configuration(self.tmp_dir)
        mock_configuration.return_value = config
        mock_formatter = MagicMock()
        mock_formatter_cls.return_value = mock_formatter
        mock_handler = MagicMock()
        mock_handler_cls.return_value = mock_handler

        handler = LogHandler()

        log_cfg = config.get_cfg_metadata().logs
        expected_filepath = Path(self.tmp_dir) / log_cfg.dir_name / f"{log_cfg.filename}.{log_cfg.extension}"
        mock_handler_cls.assert_called_once_with(
            expected_filepath,
            when="W0",
            interval=1,
            backupCount=4,
            encoding="utf-8",
            utc=True,
        )
        mock_handler.setFormatter.assert_called_once_with(mock_formatter)
        self.assertIs(handler.file_handler, mock_handler)

    @patch("scanbackup.shared.outputs.logs.logging.basicConfig")
    @patch("scanbackup.shared.outputs.logs.TimedRotatingFileHandler")
    @patch("scanbackup.shared.outputs.logs.logging.Formatter")
    @patch("scanbackup.shared.outputs.logs.Configuration")
    def test_registers_file_handler_and_logger_is_usable(
        self, mock_configuration, mock_formatter_cls, mock_handler_cls, mock_basic_config
    ) -> None:
        """The rotating handler must be wired into logging.basicConfig and the resulting logger must work."""
        config = self._mock_configuration(self.tmp_dir)
        mock_configuration.return_value = config
        mock_handler = MagicMock()
        mock_handler_cls.return_value = mock_handler

        handler = LogHandler()

        mock_basic_config.assert_called_once_with(level=logging.INFO, handlers=[mock_handler])
        self.assertIsInstance(handler.logger, logging.Logger)
        self.assertEqual(handler.logger.name, "scanbackup.shared.outputs.logs")
        handler.logger.info("test message")

    def test_module_level_log_export_is_usable(self) -> None:
        """The Log singleton exported at module import time must be a real, usable logger."""
        from scanbackup.shared.outputs.logs import Log, LOG_HANDLER

        self.assertIs(Log, LOG_HANDLER.logger)
        self.assertIsInstance(Log, logging.Logger)
        Log.info("module level log usability check")


if __name__ == "__main__":
    import unittest

    unittest.main()
