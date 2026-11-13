from datetime import UTC, date, datetime, timedelta

from traffic_collector.clock import TargetDate
from traffic_collector.domain import Sample
from traffic_collector.parsing import DayFilter

TARGET = TargetDate.previous_day(date(2026, 11, 6))
MIDNIGHT_CARACAS_UTC = datetime(2026, 11, 5, 4, 0, tzinfo=UTC)


def sample_at(moment: datetime) -> Sample:
    """Build a sample with fixed values at `moment`."""
    return Sample(ts=moment, in_avg=1.0, out_avg=2.0, in_max=3.0, out_max=4.0)


def test_midnight_of_the_target_day_is_kept() -> None:
    """00:00:00 of the target day in Caracas enters (RF-023)."""
    kept = DayFilter(TARGET).apply((sample_at(MIDNIGHT_CARACAS_UTC),))

    assert len(kept) == 1


def test_midnight_of_the_next_day_is_discarded() -> None:
    """00:00:00 of the following day in Caracas does not enter (RF-023)."""
    next_midnight = MIDNIGHT_CARACAS_UTC + timedelta(days=1)

    assert DayFilter(TARGET).apply((sample_at(next_midnight),)) == ()


def test_last_sample_of_the_day_is_kept() -> None:
    """23:55:00 of the target day in Caracas enters (RF-023)."""
    last_sample = MIDNIGHT_CARACAS_UTC + timedelta(hours=23, minutes=55)

    assert len(DayFilter(TARGET).apply((sample_at(last_sample),))) == 1


def test_sample_before_the_target_day_is_discarded() -> None:
    """The last sample of the day before does not enter (RF-023)."""
    previous = MIDNIGHT_CARACAS_UTC - timedelta(minutes=5)

    assert DayFilter(TARGET).apply((sample_at(previous),)) == ()


def test_values_and_order_are_not_modified() -> None:
    """Kept samples are the same objects in the same order (RF-023)."""
    first = sample_at(MIDNIGHT_CARACAS_UTC)
    second = sample_at(MIDNIGHT_CARACAS_UTC + timedelta(minutes=5))
    outside = sample_at(MIDNIGHT_CARACAS_UTC + timedelta(days=2))

    assert DayFilter(TARGET).apply((first, outside, second)) == (first, second)
