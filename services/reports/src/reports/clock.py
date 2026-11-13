from abc import ABC, abstractmethod
from datetime import date, datetime

from reports.constants.constants import CARACAS_TIMEZONE


class Clock(ABC):
    """Source of the current time in America/Caracas, injected so that dates can be tested."""

    @abstractmethod
    def now(self) -> datetime:
        """Return the current timezone-aware moment in America/Caracas."""

    def today(self) -> date:
        """Return the current day in America/Caracas."""
        return self.now().date()


class SystemClock(Clock):
    """Clock backed by the system time."""

    def now(self) -> datetime:
        return datetime.now(CARACAS_TIMEZONE)
