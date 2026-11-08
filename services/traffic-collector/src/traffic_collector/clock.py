from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from traffic_collector.constants.constants import CARACAS_TIMEZONE_NAME, DATE_FORMAT

CARACAS_TIMEZONE = ZoneInfo(CARACAS_TIMEZONE_NAME)


@dataclass(frozen=True, slots=True)
class TargetDate:
    """The day to collect, in America/Caracas. It is calculated once and shared by all layers."""

    day: date

    @classmethod
    def previous_day(cls, today: date) -> "TargetDate":
        """Return the day before `today`; `today` is injected so the result is deterministic."""
        return cls(day=today - timedelta(days=1))

    @property
    def key(self) -> str:
        """Return the day as `YYYY-MM-DD`, the key used by the database."""
        return self.day.strftime(DATE_FORMAT)

    @property
    def start(self) -> datetime:
        """Return 00:00:00 of the day in America/Caracas (inclusive)."""
        return datetime.combine(self.day, time.min, tzinfo=CARACAS_TIMEZONE)

    @property
    def end(self) -> datetime:
        """Return 00:00:00 of the following day in America/Caracas (exclusive)."""
        return datetime.combine(self.day + timedelta(days=1), time.min, tzinfo=CARACAS_TIMEZONE)

    def contains(self, moment: datetime) -> bool:
        """Return True if the timezone-aware `moment` falls inside the day."""
        return self.start <= moment < self.end
