from abc import abstractmethod
from pymongo.database import Database
from pathlib import Path
from scanbackup.infrastructure.readers.reader import BaseReader


class CollectionOperation:
    @abstractmethod
    def create(database: Database) -> None:
        pass

    @abstractmethod
    def delete(database: Database) -> None:
        pass

    @abstractmethod
    def export_data(
        database: Database,
        output_path: Path,
        delimiter: str,
        include_id: bool = False,
    ) -> None:
        pass

    @abstractmethod
    def import_data(database: Database, input_path: Path, reader: BaseReader) -> None:
        pass
