from abc import ABC, abstractmethod
from scanbackup.domain.entities.bbip.traffic.source import BBIPTrafficSourceEntity


class TrafficBBIPSourceRepository(ABC):
    @abstractmethod
    def get_existing_keys(self) -> list[dict]:
        """Returns a list of dicts with {interface, layer, type} of all documents."""
        pass

    @abstractmethod
    def upsert_sources(self, data: list[BBIPTrafficSourceEntity]) -> None:
        """Upsert the batch. New ones are inserted, existing ones are updated."""
        pass

    @abstractmethod
    def discontinue_missing(self, present_keys: list[dict]) -> None:
        """Marks as DISCONTINUED the documents whose key is not in present_keys."""
        pass

    @abstractmethod
    def get_sources_by_layer(self, layer: str) -> list[BBIPTrafficSourceEntity]:
        """Returns all source data of  a layer."""
        pass
