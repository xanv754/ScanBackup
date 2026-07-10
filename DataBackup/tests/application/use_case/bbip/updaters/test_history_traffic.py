from unittest.mock import MagicMock, patch
from bson import ObjectId
from scanbackup.application.use_case.bbip.updaters.history_traffic import (
    TrafficHistoryUpdaterUseCase,
)
from scanbackup.domain import TrafficSourceBBIPEntity
from scanbackup.shared import DataNotFoundError
from tests.support import TempDirTestCase

MODULE = "scanbackup.application.use_case.bbip.updaters.history_traffic"
SCAN_HEADER_LINE = "Interface;Capacity;Model;Date;Time;In_Prom;Out_Prom;In_Max;Out_Max;Layer"


class TestTrafficHistoryUpdaterUseCase(TempDirTestCase):
    """Unit tests for the TrafficHistoryUpdaterUseCase."""

    def _mock_configuration(self) -> MagicMock:
        """Build a fake Configuration pointing the scanner storage to tmp_dir."""
        scanner = MagicMock()
        scanner.file_delimiter = ";"
        scanner.date_format = "%Y-%m-%d"
        scanner.dir_storage = "traffic"
        metadata = MagicMock()
        metadata.dir_data = "data"
        metadata.scanner = scanner
        config = MagicMock()
        config.get_projectpath.return_value = str(self.tmp_dir)
        config.get_cfg_metadata.return_value = metadata
        return config

    def _build_use_case(self) -> TrafficHistoryUpdaterUseCase:
        """Build a use case wired with mocked repositories."""
        self.history_repo = MagicMock()
        self.source_repo = MagicMock()
        self.daily_repo = MagicMock()
        return TrafficHistoryUpdaterUseCase(
            layer="BORDE",
            history_repository=self.history_repo,
            source_repository=self.source_repo,
            daily_repository=self.daily_repo,
            data_date="2026-01-01",
        )

    def _write_traffic_file(self, storage_dir, row: str) -> None:
        """Write a single-row SCAN traffic file with the expected header."""
        storage_dir.mkdir(parents=True, exist_ok=True)
        (storage_dir / "traffic.csv").write_text(
            f"{SCAN_HEADER_LINE}\n{row}\n", encoding="utf-8"
        )

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_bbip")
    @patch(f"{MODULE}.Configuration")
    def test_execute_inserts_history_and_triggers_daily_summary(
        self, mock_configuration, mock_valid_layer
    ) -> None:
        """A matching traffic row must be inserted and roll into the daily summary."""
        mock_configuration.return_value = self._mock_configuration()
        mock_valid_layer.return_value = True
        storage_dir = self.tmp_dir / "data" / "traffic"
        self._write_traffic_file(
            storage_dir,
            "Gi0/0/0;1000;Cisco;2026-01-01;10:00:00;100;50;200;100;BORDE",
        )
        device_id = str(ObjectId())
        source = TrafficSourceBBIPEntity(
            device=device_id,
            link="http://example.com",
            interface="Gi0/0/0",
            capacity=1000.0,
            model="Cisco",
            layer="BORDE",
        )
        use_case = self._build_use_case()
        self.source_repo.get_sources_by_layer_id.return_value = [source]

        use_case.execute()

        self.history_repo.insert.assert_called_once()
        entities = self.history_repo.insert.call_args[0][0]
        self.assertEqual(len(entities), 1)
        self.assertEqual(str(entities[0].device), device_id)
        self.daily_repo.insert.assert_called_once()

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_bbip")
    @patch(f"{MODULE}.Configuration")
    def test_execute_skips_rows_from_a_different_date(
        self, mock_configuration, mock_valid_layer
    ) -> None:
        """A row whose date does not match the target date must be ignored entirely."""
        mock_configuration.return_value = self._mock_configuration()
        mock_valid_layer.return_value = True
        storage_dir = self.tmp_dir / "data" / "traffic"
        self._write_traffic_file(
            storage_dir,
            "Gi0/0/0;1000;Cisco;2025-12-31;10:00:00;100;50;200;100;BORDE",
        )
        use_case = self._build_use_case()
        self.source_repo.get_sources_by_layer_id.return_value = []

        use_case.execute()

        self.history_repo.insert.assert_not_called()
        self.daily_repo.insert.assert_not_called()

    @patch(f"{MODULE}.Configuration")
    def test_missing_storage_directory_raises_data_not_found_error(
        self, mock_configuration
    ) -> None:
        """A non-existent scanner storage directory must raise DataNotFoundError."""
        mock_configuration.return_value = self._mock_configuration()
        use_case = self._build_use_case()

        with self.assertRaises(DataNotFoundError):
            use_case.execute()


if __name__ == "__main__":
    import unittest

    unittest.main()
