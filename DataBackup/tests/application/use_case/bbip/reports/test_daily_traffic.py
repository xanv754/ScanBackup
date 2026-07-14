import unittest
from datetime import date
from unittest.mock import MagicMock, patch
from bson import ObjectId
from scanbackup.application.use_case.bbip.reports.daily_traffic import (
    TrafficDailyReportGeneratorUseCase,
)
from scanbackup.domain import TrafficSourceBBIPEntity, TrafficDailySummaryBBIPEntity
from scanbackup.shared import ExcelExportError, ExportError

ADAPTER_MODULE = "scanbackup.application.adapters.bbip.reports.traffic_report"


def _source(interface: str, layer: str, source_id: ObjectId | None = None) -> TrafficSourceBBIPEntity:
    """Build a valid active traffic source entity for use-case tests."""
    return TrafficSourceBBIPEntity(
        id=source_id or ObjectId(),
        link=f"http://example.com/{interface}",
        interface=interface,
        capacity=1000.0,
        model="Cisco",
        layer=layer,
    )


def _summary(device: ObjectId) -> TrafficDailySummaryBBIPEntity:
    """Build a single daily traffic summary for a device."""
    return TrafficDailySummaryBBIPEntity(
        date=date(2026, 1, 1),
        in_prom=1.0,
        in_max=2.0,
        out_prom=1.5,
        out_max=2.5,
        use=50.0,
        device=device,
    )


class TestTrafficDailyReportGeneratorUseCase(unittest.TestCase):
    """Unit tests for the TrafficDailyReportGeneratorUseCase."""

    def setUp(self) -> None:
        """Build a use case wired with mocked repositories."""
        self.source_repo = MagicMock()
        self.daily_repo = MagicMock()

    def _build_use_case(self, layers: list[str]) -> TrafficDailyReportGeneratorUseCase:
        """Build a use case instance sharing this test's mocked collaborators."""
        return TrafficDailyReportGeneratorUseCase(
            source_repository=self.source_repo,
            daily_repository=self.daily_repo,
            layers=layers,
            data_date="2026-01-01",
            filename="ScanBackup_2026-01-01",
        )

    @patch(f"{ADAPTER_MODULE}.ExcelWriter")
    def test_execute_joins_summaries_with_active_sources_and_exports(
        self, mock_writer_cls
    ) -> None:
        """execute() must join each summary with its active source and export the resulting rows."""
        source = _source("Gi0/0/0", "BORDE")
        self.source_repo.get_all_active_sources.return_value = [source]
        self.daily_repo.get_by_date.return_value = [_summary(source.id)]
        writer = MagicMock()
        writer.export.return_value = "/tmp/ScanBackup_2026-01-01.xlsx"
        mock_writer_cls.return_value = writer

        result = self._build_use_case(["BORDE"]).execute()

        self.assertEqual(result, "/tmp/ScanBackup_2026-01-01.xlsx")
        writer.export.assert_called_once()
        rows = writer.export.call_args.kwargs["data"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].interface, "Gi0/0/0")
        self.assertEqual(rows[0].layer, "BORDE")
        self.assertEqual(writer.export.call_args.kwargs["sheet_names"], ["BORDE"])

    @patch(f"{ADAPTER_MODULE}.ExcelWriter")
    def test_lowercase_configured_layers_still_match_uppercase_stored_sources(
        self, mock_writer_cls
    ) -> None:
        """Configured layers in any casing must be uppercased to match stored (uppercase) source layers."""
        source = _source("Gi0/0/0", "BORDE")
        self.source_repo.get_all_active_sources.return_value = [source]
        self.daily_repo.get_by_date.return_value = [_summary(source.id)]
        writer = MagicMock()
        mock_writer_cls.return_value = writer

        self._build_use_case(["borde"]).execute()

        self.assertEqual(writer.export.call_args.kwargs["sheet_names"], ["BORDE"])
        rows = writer.export.call_args.kwargs["data"]
        self.assertEqual(len(rows), 1)

    @patch(f"{ADAPTER_MODULE}.ExcelWriter")
    def test_execute_drops_summaries_whose_source_is_not_active(
        self, mock_writer_cls
    ) -> None:
        """A summary whose device has no matching active source must be dropped."""
        self.source_repo.get_all_active_sources.return_value = []
        self.daily_repo.get_by_date.return_value = [_summary(ObjectId())]
        writer = MagicMock()
        mock_writer_cls.return_value = writer

        self._build_use_case(["BORDE"]).execute()

        rows = writer.export.call_args.kwargs["data"]
        self.assertEqual(rows, [])

    @patch(f"{ADAPTER_MODULE}.ExcelWriter")
    def test_excel_export_error_is_propagated_unwrapped(self, mock_writer_cls) -> None:
        """An ExcelExportError raised by the writer must propagate without double-wrapping."""
        self.source_repo.get_all_active_sources.return_value = []
        self.daily_repo.get_by_date.return_value = []
        writer = MagicMock()
        writer.export.side_effect = ExcelExportError()
        mock_writer_cls.return_value = writer

        with self.assertRaises(ExcelExportError):
            self._build_use_case(["BORDE"]).execute()

    def test_unexpected_error_is_wrapped_into_export_error(self) -> None:
        """Any other unexpected failure must be wrapped into ExportError."""
        self.source_repo.get_all_active_sources.side_effect = RuntimeError("boom")

        with self.assertRaises(ExportError):
            self._build_use_case(["BORDE"]).execute()


if __name__ == "__main__":
    unittest.main()
