from abc import ABC, abstractmethod
from datetime import date
from scanbackup.domain.entities.bbip.ip.data import IPActiveBBIPEntity


class IPHistoryBBIPRepository(ABC):
    @abstractmethod
    def insert(self, data: list[IPActiveBBIPEntity]) -> None:
        """Persist a batch of 5-minute IP active samples."""
        pass

    @abstractmethod
    def get_by_date(self, target_date: date) -> list[IPActiveBBIPEntity]:
        """Retrieve every 5-minute active-IP sample recorded on `target_date`."""
        pass
