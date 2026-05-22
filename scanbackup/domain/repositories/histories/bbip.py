from abc import ABC, abstractmethod
from domain.entities.history import BBIPEntity


class BBIPRepository(ABC):
    @abstractmethod
    def update_info(self, table: str, data: list[BBIPEntity]) -> None:
        pass

    @abstractmethod
    def get_all(self, table: str) -> BBIPEntity:
        pass

    @abstractmethod
    def get_by_range_date(
        self,
        table: str,
        initial_date: str,
        final_date: str,
        initial_time: str | None = None,
        final_time: str | None = None,
    ) -> BBIPEntity:
        pass
