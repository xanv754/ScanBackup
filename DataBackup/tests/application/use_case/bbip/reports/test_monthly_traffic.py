import unittest
from datetime import date
from unittest.mock import MagicMock
from bson import ObjectId
from scanbackup.application.use_case.bbip.reports.monthly_traffic import (
    TrafficMonthlyReportGeneratorUseCase,
)
from scanbackup.domain import TrafficSourceBBIPEntity, TrafficDailySummaryBBIPEntity
from scanbackup.shared import ExcelExportError, ExportError


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


def _summary(device: ObjectId, day: int, **overrides) -> TrafficDailySummaryBBIPEntity:
    """Build a single daily traffic summary for a device on a given day of January 2026."""
    payload = {
        "date": date(2026, 1, day),
        "in_prom": 10.0,
        "in_max": 20.0,
        "out_prom": 5.0,
        "out_max": 15.0,
        "use": 50.0,
        "device": device,
    }
    payload.update(overrides)
    return TrafficDailySummaryBBIPEntity(**payload)


class TestTrafficMonthlyReportGeneratorUseCase(unittest.TestCase):
    """Unit tests for the TrafficMonthlyReportGeneratorUseCase."""

    def setUp(self) -> None:
        """Build a use case wired with mocked repositories and exporter."""
        self.source_repo = MagicMock()
        self.daily_repo = MagicMock()
        self.report_exporter = MagicMock()

    def _build_use_case(
        self, layers: list[str], year: int = 2026, month: int = 1
    ) -> TrafficMonthlyReportGeneratorUseCase:
        """Build a use case instance sharing this test's mocked collaborators."""
        return TrafficMonthlyReportGeneratorUseCase(
            source_repository=self.source_repo,
            daily_repository=self.daily_repo,
            report_exporter=self.report_exporter,
            layers=layers,
            year=year,
            month=month,
            filename="ScanBackup_2026-01",
        )

    def test_queries_the_full_month_date_range(self) -> None:
        """execute() must query daily summaries from the 1st to the last day of the month."""
        self.daily_repo.get_by_date_range.return_value = []
        self.source_repo.get_all_active_sources.return_value = []

        self._build_use_case(["BORDE"], year=2026, month=2).execute()

        self.daily_repo.get_by_date_range.assert_called_once_with(
            date(2026, 2, 1), date(2026, 2, 28)
        )

    def test_leap_year_february_includes_the_29th(self) -> None:
        """A leap year's February must span through the 29th."""
        self.daily_repo.get_by_date_range.return_value = []
        self.source_repo.get_all_active_sources.return_value = []

        self._build_use_case(["BORDE"], year=2028, month=2).execute()

        self.daily_repo.get_by_date_range.assert_called_once_with(
            date(2028, 2, 1), date(2028, 2, 29)
        )

    def test_averages_prom_and_keeps_the_highest_max_and_use(self) -> None:
        """Prom values must be averaged; max and use values must keep the highest recorded."""
        source = _source("Gi0/0/0", "BORDE")
        self.source_repo.get_all_active_sources.return_value = [source]
        self.daily_repo.get_by_date_range.return_value = [
            _summary(source.id, 1, in_prom=10.0, out_prom=4.0, in_max=20.0, out_max=15.0, use=40.0),
            _summary(source.id, 2, in_prom=20.0, out_prom=6.0, in_max=30.0, out_max=10.0, use=60.0),
        ]
        self.report_exporter.export.return_value = "/tmp/ScanBackup_2026-01.xlsx"

        result = self._build_use_case(["BORDE"]).execute()

        self.assertEqual(result, "/tmp/ScanBackup_2026-01.xlsx")
        rows = self.report_exporter.export.call_args.args[0]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.in_prom, 15.0)
        self.assertEqual(row.out_prom, 5.0)
        self.assertEqual(row.in_max, 30.0)
        self.assertEqual(row.out_max, 15.0)
        self.assertEqual(row.use, 60.0)
        self.assertEqual(row.date, date(2026, 1, 1))

    def test_drops_summaries_whose_source_is_not_active(self) -> None:
        """A device with no matching active source must be dropped from the report."""
        self.source_repo.get_all_active_sources.return_value = []
        self.daily_repo.get_by_date_range.return_value = [_summary(ObjectId(), 1)]

        self._build_use_case(["BORDE"]).execute()

        rows = self.report_exporter.export.call_args.args[0]
        self.assertEqual(rows, [])

    def test_excel_export_error_is_propagated_unwrapped(self) -> None:
        """An ExcelExportError raised by the exporter must propagate without double-wrapping."""
        self.source_repo.get_all_active_sources.return_value = []
        self.daily_repo.get_by_date_range.return_value = []
        self.report_exporter.export.side_effect = ExcelExportError()

        with self.assertRaises(ExcelExportError):
            self._build_use_case(["BORDE"]).execute()

    def test_unexpected_error_is_wrapped_into_export_error(self) -> None:
        """Any other unexpected failure must be wrapped into ExportError."""
        self.source_repo.get_all_active_sources.side_effect = RuntimeError("boom")

        with self.assertRaises(ExportError):
            self._build_use_case(["BORDE"]).execute()


class TestTrafficMonthlyReportGeneratorUseCaseResolveLiteralRange(unittest.TestCase):
    """Unit tests for TrafficMonthlyReportGeneratorUseCase.resolve_literal_range."""

    def test_spans_the_30_trailing_days_including_the_reference_date(self) -> None:
        """Literal mode must span the 30 trailing days counting back from the reference date, inclusive."""
        reference_date = date(2026, 2, 9)

        start, end = TrafficMonthlyReportGeneratorUseCase.resolve_literal_range(
            reference_date
        )

        self.assertEqual(start, date(2026, 1, 11))
        self.assertEqual(end, date(2026, 2, 9))


class TestTrafficMonthlyReportGeneratorUseCaseLiteralMode(unittest.TestCase):
    """Unit tests for the TrafficMonthlyReportGeneratorUseCase in literal mode."""

    def setUp(self) -> None:
        """Build a use case wired with mocked repositories and exporter."""
        self.source_repo = MagicMock()
        self.daily_repo = MagicMock()
        self.report_exporter = MagicMock()

    def _build_literal_use_case(
        self, layers: list[str], reference_date: date = date(2026, 2, 9)
    ) -> TrafficMonthlyReportGeneratorUseCase:
        """Build a literal-mode use case instance sharing this test's mocked collaborators."""
        return TrafficMonthlyReportGeneratorUseCase(
            source_repository=self.source_repo,
            daily_repository=self.daily_repo,
            report_exporter=self.report_exporter,
            layers=layers,
            filename="ScanBackup_2026-01-11_2026-02-09",
            literal=True,
            reference_date=reference_date,
        )

    def test_queries_the_30_trailing_days(self) -> None:
        """execute() in literal mode must query the 30 trailing days from the reference date."""
        self.daily_repo.get_by_date_range.return_value = []
        self.source_repo.get_all_active_sources.return_value = []

        self._build_literal_use_case(["BORDE"]).execute()

        self.daily_repo.get_by_date_range.assert_called_once_with(
            date(2026, 1, 11), date(2026, 2, 9)
        )

    def test_averages_prom_and_keeps_the_highest_max_and_use(self) -> None:
        """Prom values must be averaged; max and use values must keep the highest recorded."""
        source = _source("Gi0/0/0", "BORDE")
        self.source_repo.get_all_active_sources.return_value = [source]
        self.daily_repo.get_by_date_range.return_value = [
            _summary(source.id, 1, in_prom=10.0, out_prom=4.0, in_max=20.0, out_max=15.0, use=40.0),
            _summary(source.id, 2, in_prom=20.0, out_prom=6.0, in_max=30.0, out_max=10.0, use=60.0),
        ]
        self.report_exporter.export.return_value = "/tmp/ScanBackup_2026-01-11_2026-02-09.xlsx"

        result = self._build_literal_use_case(["BORDE"]).execute()

        self.assertEqual(result, "/tmp/ScanBackup_2026-01-11_2026-02-09.xlsx")
        rows = self.report_exporter.export.call_args.args[0]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.in_prom, 15.0)
        self.assertEqual(row.out_prom, 5.0)
        self.assertEqual(row.in_max, 30.0)
        self.assertEqual(row.out_max, 15.0)
        self.assertEqual(row.use, 60.0)
        self.assertEqual(row.date, date(2026, 1, 11))


if __name__ == "__main__":
    unittest.main()
