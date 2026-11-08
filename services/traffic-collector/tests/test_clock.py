from datetime import UTC, date, datetime

from traffic_collector.clock import CARACAS_TIMEZONE, TargetDate


def test_previous_day_is_the_day_before_today() -> None:
    """The target is the day before the injected today (RF-016)."""
    assert TargetDate.previous_day(date(2026, 11, 6)).key == "2026-11-05"


def test_previous_day_crosses_month_and_year() -> None:
    """The calculation is calendar-aware (RF-016)."""
    assert TargetDate.previous_day(date(2026, 3, 1)).key == "2026-02-28"
    assert TargetDate.previous_day(date(2026, 1, 1)).key == "2025-12-31"


def test_start_is_inclusive_and_end_is_exclusive() -> None:
    """Midnight starts the day and the next midnight does not belong to it (RF-016)."""
    target = TargetDate.previous_day(date(2026, 11, 6))

    assert target.contains(datetime(2026, 11, 5, 0, 0, 0, tzinfo=CARACAS_TIMEZONE))
    assert target.contains(datetime(2026, 11, 5, 23, 55, 0, tzinfo=CARACAS_TIMEZONE))
    assert not target.contains(datetime(2026, 11, 6, 0, 0, 0, tzinfo=CARACAS_TIMEZONE))
    assert not target.contains(datetime(2026, 11, 4, 23, 59, 59, tzinfo=CARACAS_TIMEZONE))


def test_contains_uses_caracas_offset_for_utc_moments() -> None:
    """A UTC moment is compared in Caracas time (UTC-4) (RF-016)."""
    target = TargetDate.previous_day(date(2026, 11, 6))

    assert target.contains(datetime(2026, 11, 5, 4, 0, 0, tzinfo=UTC))
    assert not target.contains(datetime(2026, 11, 5, 3, 59, 59, tzinfo=UTC))
    assert not target.contains(datetime(2026, 11, 6, 4, 0, 0, tzinfo=UTC))
