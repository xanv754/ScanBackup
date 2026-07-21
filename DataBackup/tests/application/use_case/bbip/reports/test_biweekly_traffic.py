import unittest
from datetime import date
from unittest.mock import MagicMock, patch
from bson import ObjectId
from scanbackup.application.use_case.bbip.reports.biweekly_traffic import (
    TrafficBiweeklyReportGeneratorUseCase,
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


def _summary(device: ObjectId, day: date, **overrides) -> TrafficDailySummaryBBIPEntity:
    """Build a single daily traffic summary for a device on a given day."""
    payload = {
        "date": day,
        "in_prom": 10.0,
        "in_max": 20.0,
        "out_prom": 5.0,
        "out_max": 15.0,
        "use": 50.0,
        "device": device,
    }
    payload.update(overrides)
    return TrafficDailySummaryBBIPEntity(**payload)


class TestTrafficBiweeklyReportGeneratorUseCaseResolveBiweeklyRange(unittest.TestCase):
    """Unit tests for TrafficBiweeklyReportGeneratorUseCase.resolve_biweekly_range."""

    def test_default_mode_spans_the_1st_through_the_15th_of_the_reference_dates_month(
        self,
    ) -> None:
        """Default (non-literal) mode must span from the 1st through the 15th of the reference date's month."""
        reference_date = date(2026, 2, 9)

        start, end = TrafficBiweeklyReportGeneratorUseCase.resolve_biweekly_range(
            reference_date, literal=False
        )

        self.assertEqual(start, date(2026, 2, 1))
        self.assertEqual(end, date(2026, 2, 15))

    def test_literal_mode_spans_the_15_trailing_days_including_the_reference_date(
        self,
    ) -> None:
        """Literal mode must span the 15 trailing days counting back from the reference date, inclusive."""
        reference_date = date(2026, 2, 9)

        start, end = TrafficBiweeklyReportGeneratorUseCase.resolve_biweekly_range(
            reference_date, literal=True
        )

        self.assertEqual(start, date(2026, 1, 26))
        self.assertEqual(end, date(2026, 2, 9))


class TestTrafficBiweeklyReportGeneratorUseCase(unittest.TestCase):
    """Unit tests for the TrafficBiweeklyReportGeneratorUseCase."""

    def setUp(self) -> None:
        """Build a use case wired with mocked repositories."""
        self.source_repo = MagicMock()
        self.daily_repo = MagicMock()

    def _build_use_case(
        self, layers: list[str], reference_date: date = date(2026, 2, 9), literal: bool = False
    ) -> TrafficBiweeklyReportGeneratorUseCase:
        """Build a use case instance sharing this test's mocked collaborators."""
        return TrafficBiweeklyReportGeneratorUseCase(
            source_repository=self.source_repo,
            daily_repository=self.daily_repo,
            layers=layers,
            reference_date=reference_date,
            filename="ScanBackup_2026-02-01_2026-02-15",
            literal=literal,
        )

    def test_queries_the_resolved_biweekly_date_range(self) -> None:
        """execute() must query daily summaries between the resolved start and end dates."""
        self.daily_repo.get_by_date_range.return_value = []
        self.source_repo.get_all_active_sources.return_value = []

        with patch(f"{ADAPTER_MODULE}.ExcelWriter"):
            self._build_use_case(["BORDE"]).execute()

        self.daily_repo.get_by_date_range.assert_called_once_with(
            date(2026, 2, 1), date(2026, 2, 15)
        )

    def test_literal_mode_queries_the_15_trailing_days(self) -> None:
        """execute() in literal mode must query the 15 trailing days from the reference date."""
        self.daily_repo.get_by_date_range.return_value = []
        self.source_repo.get_all_active_sources.return_value = []

        with patch(f"{ADAPTER_MODULE}.ExcelWriter"):
            self._build_use_case(["BORDE"], literal=True).execute()

        self.daily_repo.get_by_date_range.assert_called_once_with(
            date(2026, 1, 26), date(2026, 2, 9)
        )

    @patch(f"{ADAPTER_MODULE}.ExcelWriter")
    def test_averages_prom_and_keeps_the_highest_max_and_use(
        self, mock_writer_cls
    ) -> None:
        """Prom values must be averaged; max and use values must keep the highest recorded."""
        source = _source("Gi0/0/0", "BORDE")
        self.source_repo.get_all_active_sources.return_value = [source]
        self.daily_repo.get_by_date_range.return_value = [
            _summary(source.id, date(2026, 2, 1), in_prom=10.0, out_prom=4.0, in_max=20.0, out_max=15.0, use=40.0),
            _summary(source.id, date(2026, 2, 2), in_prom=20.0, out_prom=6.0, in_max=30.0, out_max=10.0, use=60.0),
        ]
        writer = MagicMock()
        writer.export.return_value = "/tmp/ScanBackup_2026-02-01_2026-02-15.xlsx"
        mock_writer_cls.return_value = writer

        result = self._build_use_case(["BORDE"]).execute()

        self.assertEqual(result, "/tmp/ScanBackup_2026-02-01_2026-02-15.xlsx")
        rows = writer.export.call_args.kwargs["data"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.in_prom, 15.0)
        self.assertEqual(row.out_prom, 5.0)
        self.assertEqual(row.in_max, 30.0)
        self.assertEqual(row.out_max, 15.0)
        self.assertEqual(row.use, 60.0)
        self.assertEqual(row.date, date(2026, 2, 1))

    @patch(f"{ADAPTER_MODULE}.ExcelWriter")
    def test_drops_summaries_whose_source_is_not_active(self, mock_writer_cls) -> None:
        """A device with no matching active source must be dropped from the report."""
        self.source_repo.get_all_active_sources.return_value = []
        self.daily_repo.get_by_date_range.return_value = [
            _summary(ObjectId(), date(2026, 2, 1))
        ]
        writer = MagicMock()
        mock_writer_cls.return_value = writer

        self._build_use_case(["BORDE"]).execute()

        rows = writer.export.call_args.kwargs["data"]
        self.assertEqual(rows, [])

    @patch(f"{ADAPTER_MODULE}.ExcelWriter")
    def test_excel_export_error_is_propagated_unwrapped(self, mock_writer_cls) -> None:
        """An ExcelExportError raised by the writer must propagate without double-wrapping."""
        self.source_repo.get_all_active_sources.return_value = []
        self.daily_repo.get_by_date_range.return_value = []
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
