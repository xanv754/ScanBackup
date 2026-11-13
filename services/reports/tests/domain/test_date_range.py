from datetime import date, datetime

import pytest

from reports.constants.constants import CARACAS_TIMEZONE
from reports.domain.date_range import DateRange, DateRangeValidator
from reports.exceptions import InvalidInputError
from tests.fakes import FixedClock


def validate_causes(
    clock: FixedClock, start: str | None, end: str | None, extras: tuple[str, ...] = ()
) -> list[str]:
    """Validate expecting failure and return the causes."""
    with pytest.raises(InvalidInputError) as error_info:
        DateRangeValidator(clock).validate(start, end, extras)
    return error_info.value.causes


def test_rf033_valid_range_is_built(clock: FixedClock) -> None:
    """RF-033: a valid range keeps both ends."""
    date_range = DateRangeValidator(clock).validate("2026-11-01", "2026-11-09", ())
    assert date_range == DateRange(start=date(2026, 11, 1), end=date(2026, 11, 9))


def test_rf033_single_day_is_valid(clock: FixedClock) -> None:
    """RF-033: start equal to end is a one-day range."""
    date_range = DateRangeValidator(clock).validate("2026-11-05", "2026-11-05", ())
    assert date_range.day_count == 1
    assert date_range.day_keys() == ("2026-11-05",)


def test_rf033_day_count_includes_both_ends(clock: FixedClock) -> None:
    """RF-033: the number of days is (end - start) + 1."""
    date_range = DateRangeValidator(clock).validate("2026-02-27", "2026-03-02", ())
    assert date_range.day_count == 4
    assert date_range.day_keys() == ("2026-02-27", "2026-02-28", "2026-03-01", "2026-03-02")


@pytest.mark.parametrize("missing", [None, "", "   "])
def test_rf033_missing_or_empty_option_is_invalid(clock: FixedClock, missing: str | None) -> None:
    """RF-033: an absent or empty option is a cause, each one on its own."""
    causes = validate_causes(clock, missing, missing)
    assert causes == ["Falta la opción --start", "Falta la opción --end"]


@pytest.mark.parametrize(
    "text", ["2026-1-5", "20260105", "2026/01/05", "05-01-2026", "abc", " 2026-01-05"]
)
def test_rf033_format_must_be_strict(clock: FixedClock, text: str) -> None:
    """RF-033: only `YYYY-MM-DD` is accepted (`strptime` alone would accept `2026-1-5`)."""
    causes = validate_causes(clock, text, "2026-11-09")
    assert causes == ["--start debe tener el formato YYYY-MM-DD"]


def test_rf033_nonexistent_date_is_invalid(clock: FixedClock) -> None:
    """RF-033: a well-formed but nonexistent date is invalid."""
    causes = validate_causes(clock, "2026-02-30", "2026-11-09")
    assert causes == ["--start no es una fecha existente: 2026-02-30"]


def test_rf033_start_after_end_is_invalid(clock: FixedClock) -> None:
    """RF-033: --start cannot be later than --end."""
    causes = validate_causes(clock, "2026-11-08", "2026-11-01")
    assert causes == ["--start no puede ser posterior a --end"]


@pytest.mark.parametrize("end", ["2026-11-10", "2026-11-11", "2027-01-01"])
def test_rf033_end_must_be_before_today(clock: FixedClock, end: str) -> None:
    """RF-033: --end equal to today or in the future is invalid (today is 2026-11-10)."""
    assert validate_causes(clock, "2026-11-01", end) == ["--end debe ser anterior al día actual"]


def test_rf033_yesterday_is_valid(clock: FixedClock) -> None:
    """RF-033: the day before today is the latest valid --end."""
    assert DateRangeValidator(clock).validate("2026-11-09", "2026-11-09", ()).end == date(
        2026, 11, 9
    )


def test_rf033_today_is_calculated_in_caracas() -> None:
    """RF-033: 2026-11-11 01:00 in Caracas is already the 11th, even if it is the 10th in US."""
    early_morning = FixedClock(datetime(2026, 11, 11, 1, 0, tzinfo=CARACAS_TIMEZONE))
    assert validate_causes(early_morning, "2026-11-01", "2026-11-11") == [
        "--end debe ser anterior al día actual"
    ]
    assert (
        DateRangeValidator(early_morning).validate("2026-11-01", "2026-11-10", ()).day_count == 10
    )


def test_rf033_unrecognized_options_are_causes(clock: FixedClock) -> None:
    """RF-033: every unrecognized option is reported."""
    causes = validate_causes(clock, "2026-11-01", "2026-11-09", ("--layer", "BORDE"))
    assert causes == ["Opción no reconocida: --layer", "Opción no reconocida: BORDE"]


def test_rf033_all_causes_are_accumulated(clock: FixedClock) -> None:
    """RF-033: every detectable cause is reported together."""
    causes = validate_causes(clock, "2026-1-5", "2026-11-10", ("--extra",))
    assert causes == [
        "--start debe tener el formato YYYY-MM-DD",
        "--end debe ser anterior al día actual",
        "Opción no reconocida: --extra",
    ]
