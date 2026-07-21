from abc import ABC, abstractmethod
from datetime import date
from scanbackup.domain.entities.bbip.traffic.summaries.daily import (
    TrafficDailySummaryBBIPEntity,
)
from scanbackup.domain.entities.bbip.traffic.summaries.hour import (
    TrafficHourSummaryBBIPEntity,
)


class TrafficDailySummaryBBIPRepository(ABC):
    @abstractmethod
    def insert(self, data: list[TrafficDailySummaryBBIPEntity]) -> None:
        """Persist a batch of daily traffic summaries."""
        pass

    @abstractmethod
    def get_by_date(self, target_date: date) -> list[TrafficDailySummaryBBIPEntity]:
        """Retrieve every device's daily traffic summary recorded on `target_date`."""
        pass

    @abstractmethod
    def get_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[TrafficDailySummaryBBIPEntity]:
        """Retrieve every device's daily traffic summary recorded between `start_date` and `end_date`, inclusive."""
        pass


class TrafficHourSummaryBBIPRepository(ABC):
    @abstractmethod
    def insert(self, data: list[TrafficHourSummaryBBIPEntity]) -> None:
        """Persist a batch of hourly traffic summaries."""
        pass
