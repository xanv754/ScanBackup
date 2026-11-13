from datetime import UTC, date, datetime, timedelta

import pytest
from bson import ObjectId

from tests.collection.fakes import RecordingSink
from traffic_collector.clock import TargetDate
from traffic_collector.collection import DailySummaryCalculator, DailySummaryPhase
from traffic_collector.domain import DailySummary, DailyTraffic, Sample
from traffic_collector.exceptions import DatabaseError
from traffic_collector.reporting.events import SummaryFailed, SummaryFinished

TARGET = TargetDate(date(2026, 11, 5))
START = datetime(2026, 11, 5, 4, 0, tzinfo=UTC)
FACTOR = 8.022


def make_daily(*values: tuple[float, float, float, float]) -> DailyTraffic:
    samples = tuple(
        Sample(START + timedelta(minutes=5 * index), *value)
        for index, value in enumerate(values)
    )
    return DailyTraffic(ObjectId(), "BORDE", TARGET.key, samples)


def test_averages_are_the_mean_and_maximums_the_max_with_the_factor() -> None:
    """Averages use the mean, maximums the max (never averaged), all times the factor (RF-026)."""
    daily = make_daily((100.0, 10.0, 300.0, 30.0), (200.0, 30.0, 500.0, 20.0))

    summary = DailySummaryCalculator().calculate(daily)

    assert summary.in_avg == pytest.approx(150.0 * FACTOR)
    assert summary.out_avg == pytest.approx(20.0 * FACTOR)
    assert summary.in_max == pytest.approx(500.0 * FACTOR)
    assert summary.out_max == pytest.approx(30.0 * FACTOR)
    assert (summary.interface_id, summary.date) == (daily.interface_id, daily.date)


def test_legacy_factor_in_gbps_matches_the_stored_bps() -> None:
    """The stored bps divided by 1e9 equals the legacy value raw * 0.000000008022 (RF-026)."""
    summary = DailySummaryCalculator().calculate(
        make_daily((1_000_000.0, 0.0, 2_000_000.0, 0.0))
    )

    assert summary.in_max / 1e9 == pytest.approx(2_000_000.0 * 0.000000008022)


def test_a_day_without_samples_has_no_summary() -> None:
    assert DailySummaryCalculator().calculate(make_daily()) is None


class FakeTrafficReader:
    def __init__(self, days: list[DailyTraffic]) -> None:
        self._days = days

    def daily_by_date(self, date: str):
        return iter(self._days)


class FakeSummaryWriter:
    def __init__(
        self, existing: set[ObjectId] = frozenset(), fail: bool = False
    ) -> None:
        self.existing = set(existing)
        self.fail = fail
        self.saved: list[DailySummary] = []

    def interface_ids_with_summary(self, date: str) -> set[ObjectId]:
        return self.existing

    def save(self, summary: DailySummary) -> None:
        if self.fail:
            raise DatabaseError("save")
        self.saved.append(summary)


def run_phase(days: list[DailyTraffic], writer: FakeSummaryWriter):
    sink = RecordingSink()
    phase = DailySummaryPhase(
        FakeTrafficReader(days), writer, DailySummaryCalculator(), sink
    )
    return phase.run(TARGET), sink


def test_phase_summarizes_new_days_and_skips_existing_and_empty() -> None:
    """Only days without summary and with samples are written (RF-026)."""
    new, existing, empty = (
        make_daily((1, 1, 1, 1)),
        make_daily((1, 1, 1, 1)),
        make_daily(),
    )
    writer = FakeSummaryWriter(existing={existing.interface_id})

    result, sink = run_phase([new, existing, empty], writer)

    assert not result.failed
    assert [summary.interface_id for summary in writer.saved] == [new.interface_id]
    assert sink.of_type(SummaryFinished)[0].generated_count == 1
    assert sink.of_type(SummaryFinished)[0].skipped_count == 2


def test_phase_database_error_fails_the_summary() -> None:
    """A database error stops the phase and makes it fail (RF-026)."""
    result, sink = run_phase([make_daily((1, 1, 1, 1))], FakeSummaryWriter(fail=True))

    assert result.failed
    assert len(sink.of_type(SummaryFailed)) == 1
    assert not sink.of_type(SummaryFinished)
