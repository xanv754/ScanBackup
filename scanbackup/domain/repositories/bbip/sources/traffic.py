from abc import ABC, abstractmethod
from scanbackup.domain.entities.bbip.traffic.source import BBIPTrafficSourceEntity


class TrafficBBIPSourceRepository(ABC):
    @abstractmethod
    def get_existing_keys(self) -> list[dict]:
        pass

    @abstractmethod
    def upsert_sources(self, data: list[BBIPTrafficSourceEntity]) -> None:
        pass

    @abstractmethod
    def discontinue_missing(self, present_keys: list[dict]) -> None:
        pass
