import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from scanbackup.application.cli.sources.extract_db import (
    traffic_export_from_database,
    ip_export_from_database,
)

MODULE = "scanbackup.application.cli.sources.extract_db"


@patch(f"{MODULE}.Terminal")
@patch(f"{MODULE}.Log")
class TestTrafficExportFromDatabase(unittest.TestCase):
    """Unit tests for the traffic_export_from_database CLI orchestration function."""

    @patch(f"{MODULE}.CSVWriter")
    @patch(f"{MODULE}.TrafficSourceBBIPReader")
    @patch(f"{MODULE}.TrafficSourceUpdaterUseCase")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.Configuration")
    def test_exports_all_configured_bbip_layers_when_none_given(
        self,
        mock_configuration,
        mock_repo_cls,
        mock_use_case_cls,
        mock_reader_cls,
        mock_writer_cls,
        mock_log,
        mock_terminal,
    ) -> None:
        """Without --layer, every configured BBIP layer name must be exported."""
        cfg_layers = MagicMock()
        cfg_layers.bbip.names = ["BORDE", "RAI"]
        mock_configuration.return_value.get_cfg_layers.return_value = cfg_layers
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        traffic_export_from_database(path="/tmp/out")

        use_case.export.assert_called_once_with(["BORDE", "RAI"])
        mock_use_case_cls.assert_called_once_with(
            repository=mock_repo_cls.return_value,
            path=Path("/tmp/out"),
            reader=mock_reader_cls.return_value,
            writer_factory=mock_writer_cls,
        )

    @patch(f"{MODULE}.TrafficSourceUpdaterUseCase")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.Configuration")
    def test_exports_only_the_given_layer(
        self, mock_configuration, mock_repo_cls, mock_use_case_cls, mock_log, mock_terminal
    ) -> None:
        """A given --layer must restrict the export to just that layer."""
        mock_configuration.return_value.get_cfg_layers.return_value = MagicMock()
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        traffic_export_from_database(path="/tmp/out", layer="BORDE")

        use_case.export.assert_called_once_with(["BORDE"])

    @patch(f"{MODULE}.CSVWriter")
    @patch(f"{MODULE}.TrafficSourceBBIPReader")
    @patch(f"{MODULE}.TrafficSourceUpdaterUseCase")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.Configuration")
    def test_defaults_to_home_when_no_path_given(
        self,
        mock_configuration,
        mock_repo_cls,
        mock_use_case_cls,
        mock_reader_cls,
        mock_writer_cls,
        mock_log,
        mock_terminal,
    ) -> None:
        """Without --dirpath, the export must default to the user's home directory."""
        mock_configuration.return_value.get_cfg_layers.return_value = MagicMock(
            bbip=MagicMock(names=[])
        )

        traffic_export_from_database()

        mock_use_case_cls.assert_called_once_with(
            repository=mock_repo_cls.return_value,
            path=Path.home(),
            reader=mock_reader_cls.return_value,
            writer_factory=mock_writer_cls,
        )

    @patch(f"{MODULE}.TrafficSourceUpdaterUseCase")
    @patch(f"{MODULE}.MongoTrafficSourceBBIPRepository")
    @patch(f"{MODULE}.Configuration")
    def test_failure_is_logged_without_raising(
        self, mock_configuration, mock_repo_cls, mock_use_case_cls, mock_log, mock_terminal
    ) -> None:
        """A failure during export must be reported but must not raise or exit."""
        mock_configuration.side_effect = RuntimeError("boom")

        traffic_export_from_database(path="/tmp/out")


@patch(f"{MODULE}.Terminal")
@patch(f"{MODULE}.Log")
class TestIPExportFromDatabase(unittest.TestCase):
    """Unit tests for the ip_export_from_database CLI orchestration function."""

    @patch(f"{MODULE}.CSVWriter")
    @patch(f"{MODULE}.IPSourceBBIPReader")
    @patch(f"{MODULE}.IPSourceUpdaterUseCase")
    @patch(f"{MODULE}.MongoIPSourceBBIPRepository")
    @patch(f"{MODULE}.Configuration")
    def test_exports_all_configured_ip_layers_when_none_given(
        self,
        mock_configuration,
        mock_repo_cls,
        mock_use_case_cls,
        mock_reader_cls,
        mock_writer_cls,
        mock_log,
        mock_terminal,
    ) -> None:
        """Without --layer, every configured IP layer name must be exported."""
        cfg_layers = MagicMock()
        cfg_layers.ip.names = ["IP_BRAS"]
        mock_configuration.return_value.get_cfg_layers.return_value = cfg_layers
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        ip_export_from_database(path="/tmp/out")

        use_case.export.assert_called_once_with(["IP_BRAS"])
        mock_use_case_cls.assert_called_once_with(
            repository=mock_repo_cls.return_value,
            path=Path("/tmp/out"),
            reader=mock_reader_cls.return_value,
            writer_factory=mock_writer_cls,
        )

    @patch(f"{MODULE}.IPSourceUpdaterUseCase")
    @patch(f"{MODULE}.MongoIPSourceBBIPRepository")
    @patch(f"{MODULE}.Configuration")
    def test_exports_only_the_given_layer(
        self, mock_configuration, mock_repo_cls, mock_use_case_cls, mock_log, mock_terminal
    ) -> None:
        """A given --layer must restrict the export to just that layer."""
        mock_configuration.return_value.get_cfg_layers.return_value = MagicMock()
        use_case = MagicMock()
        mock_use_case_cls.return_value = use_case

        ip_export_from_database(path="/tmp/out", layer="IP_BRAS")

        use_case.export.assert_called_once_with(["IP_BRAS"])

    @patch(f"{MODULE}.CSVWriter")
    @patch(f"{MODULE}.IPSourceBBIPReader")
    @patch(f"{MODULE}.IPSourceUpdaterUseCase")
    @patch(f"{MODULE}.MongoIPSourceBBIPRepository")
    @patch(f"{MODULE}.Configuration")
    def test_defaults_to_home_when_no_path_given(
        self,
        mock_configuration,
        mock_repo_cls,
        mock_use_case_cls,
        mock_reader_cls,
        mock_writer_cls,
        mock_log,
        mock_terminal,
    ) -> None:
        """Without --dirpath, the export must default to the user's home directory."""
        mock_configuration.return_value.get_cfg_layers.return_value = MagicMock(
            ip=MagicMock(names=[])
        )

        ip_export_from_database()

        mock_use_case_cls.assert_called_once_with(
            repository=mock_repo_cls.return_value,
            path=Path.home(),
            reader=mock_reader_cls.return_value,
            writer_factory=mock_writer_cls,
        )

    @patch(f"{MODULE}.IPSourceUpdaterUseCase")
    @patch(f"{MODULE}.MongoIPSourceBBIPRepository")
    @patch(f"{MODULE}.Configuration")
    def test_failure_is_logged_without_raising(
        self, mock_configuration, mock_repo_cls, mock_use_case_cls, mock_log, mock_terminal
    ) -> None:
        """A failure during export must be reported but must not raise or exit."""
        mock_configuration.side_effect = RuntimeError("boom")

        ip_export_from_database(path="/tmp/out")


if __name__ == "__main__":
    unittest.main()
