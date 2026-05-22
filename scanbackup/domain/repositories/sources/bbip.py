from abc import ABC, abstractmethod
from domain.entities.source import BBIPSourceEntity
from scanbackup.shared import LayerBBIP


class BBIPSourceRepository(ABC):
    @abstractmethod
    def update_info(self, data: list[BBIPSourceEntity]) -> None:
        pass

    @abstractmethod
    def get_all(self) -> list[BBIPSourceEntity]:
        pass

    @abstractmethod
    def get_source_by_layer(self, layer: LayerBBIP) -> list[BBIPSourceEntity]:
        pass
