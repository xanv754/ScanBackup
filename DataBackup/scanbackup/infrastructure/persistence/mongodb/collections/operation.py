from abc import ABC, abstractmethod
from pymongo.database import Database
from pathlib import Path


class CollectionOperation(ABC):
    @staticmethod
    @abstractmethod
    def create(database: Database) -> None:
        pass

    @staticmethod
    @abstractmethod
    def delete(database: Database) -> None:
        pass

    @staticmethod
    @abstractmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> None:
        pass

    @staticmethod
    @abstractmethod
    def import_data(database: Database, input_path: Path, delimiter: str) -> None:
        pass
