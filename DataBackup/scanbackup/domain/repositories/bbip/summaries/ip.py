from abc import ABC, abstractmethod
from scanbackup.domain.entities.bbip.ip.summaries.daily import IPDailySummaryBBIPEntity
from scanbackup.domain.entities.bbip.ip.summaries.hour import IPHourSummaryBBIPEntity


class IPDailySummaryBBIPRepository(ABC):
    @abstractmethod
    def insert(self, data: list[IPDailySummaryBBIPEntity]) -> None:
        """Persist a batch of daily IP active summaries."""
        pass


class IPHourSummaryBBIPRepository(ABC):
    @abstractmethod
    def insert(self, data: list[IPHourSummaryBBIPEntity]) -> None:
        """Persist a batch of hourly IP active summaries."""
        pass
