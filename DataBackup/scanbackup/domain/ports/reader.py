from abc import ABC, abstractmethod
from pathlib import Path


class BaseReader(ABC):
    @abstractmethod
    def import_data(self, filepath: Path) -> list[dict]:
        pass
