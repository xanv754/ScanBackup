from abc import ABC, abstractmethod
from datetime import date
from pydantic import BaseModel


class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self, source: BaseModel, target_date: date) -> list[BaseModel]:
        pass
