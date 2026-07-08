from abc import abstractmethod
from pymongo.database import Database
from pathlib import Path
from scanbackup.infrastructure.readers.reader import BaseReader


class CollectionOperation:
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
        include_id: bool = False,
    ) -> None:
        pass

    @staticmethod
    @abstractmethod
    def import_data(database: Database, input_path: Path, delimiter: str) -> None:
        pass
