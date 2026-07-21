from abc import ABC, abstractmethod
from datetime import date
from scanbackup.domain.entities.bbip.traffic.data import TrafficBBIPEntity


class TrafficHistoryBBIPRepository(ABC):
    @abstractmethod
    def insert(self, data: list[TrafficBBIPEntity]) -> None:
        """Persist a batch of 5-minute traffic samples."""
        pass

    @abstractmethod
    def get_by_date(self, target_date: date) -> list[TrafficBBIPEntity]:
        """Retrieve every 5-minute traffic sample recorded on `target_date`."""
        pass
