from abc import ABC, abstractmethod
from domain.entities.history import IPEntity


class IPRepository(ABC):
    @abstractmethod
    def update_info(self, table: str, data: list[IPEntity]) -> None:
        pass

    @abstractmethod
    def get_all(self, table: str) -> IPEntity:
        pass

    @abstractmethod
    def get_by_range_date(
        self,
        table: str,
        initial_date: str,
        final_date: str,
        initial_time: str | None = None,
        final_time: str | None = None,
    ) -> IPEntity:
        pass
