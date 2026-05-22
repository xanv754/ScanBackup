from abc import ABC, abstractmethod
from domain.entities.source import IPSourceEntity


class BBIPSourceRepository(ABC):
    @abstractmethod
    def update_info(self, data: list[IPSourceEntity]) -> None:
        pass

    @abstractmethod
    def get_all(self) -> list[IPSourceEntity]:
        pass
