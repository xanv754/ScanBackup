import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from reports.clock import Clock
from reports.constants.constants import DATE_FORMAT, DATE_PATTERN, END_OPTION, START_OPTION
from reports.exceptions import InvalidInputError


@dataclass(frozen=True, slots=True)
class DateRange:
    """The inclusive range of days of the report, in America/Caracas [RF-033]."""

    start: date
    end: date

    @property
    def day_count(self) -> int:
        """Return the number of days of the range, both ends included."""
        return (self.end - self.start).days + 1

    @property
    def start_key(self) -> str:
        """Return the first day as `YYYY-MM-DD`, the key used by the database."""
        return self.start.strftime(DATE_FORMAT)

    @property
    def end_key(self) -> str:
        """Return the last day as `YYYY-MM-DD`, the key used by the database."""
        return self.end.strftime(DATE_FORMAT)

    def day_keys(self) -> tuple[str, ...]:
        """Return every day of the range as `YYYY-MM-DD`, in chronological order."""
        return tuple(
            (self.start + timedelta(days=offset)).strftime(DATE_FORMAT)
            for offset in range(self.day_count)
        )


class DateRangeValidator:
    """Validates the `--start` and `--end` options and builds the `DateRange` [RF-033]."""

    def __init__(self, clock: Clock) -> None:
        """Receive the clock that defines today in America/Caracas."""
        self._clock = clock

    def validate(
        self, start_text: str | None, end_text: str | None, extra_arguments: Sequence[str]
    ) -> DateRange:
        """Return the range or raise `InvalidInputError` with every cause that can be detected.

        Causes: an option that is missing or empty, a text that is not a strict `YYYY-MM-DD`
        or not an existing date, `--start` after `--end`, `--end` equal or later than today,
        and unrecognized options.
        """
        causes: list[str] = []
        start = self._parse(START_OPTION, start_text, causes)
        end = self._parse(END_OPTION, end_text, causes)
        if start is not None and end is not None and start > end:
            causes.append(f"{START_OPTION} no puede ser posterior a {END_OPTION}")
        if end is not None and end >= self._clock.today():
            causes.append(f"{END_OPTION} debe ser anterior al día actual")
        causes.extend(f"Opción no reconocida: {argument}" for argument in extra_arguments)
        if causes or start is None or end is None:
            raise InvalidInputError(causes)
        return DateRange(start=start, end=end)

    @staticmethod
    def _parse(option: str, text: str | None, causes: list[str]) -> date | None:
        """Parse a strict `YYYY-MM-DD` text, recording the cause when it is invalid."""
        if text is None or not text.strip():
            causes.append(f"Falta la opción {option}")
            return None
        if not re.fullmatch(DATE_PATTERN, text):
            causes.append(f"{option} debe tener el formato YYYY-MM-DD")
            return None
        try:
            return datetime.strptime(text, DATE_FORMAT).date()
        except ValueError:
            causes.append(f"{option} no es una fecha existente: {text}")
            return None
