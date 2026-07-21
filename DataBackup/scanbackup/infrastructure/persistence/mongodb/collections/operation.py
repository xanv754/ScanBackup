from abc import ABC, abstractmethod
from pymongo.database import Database
from pathlib import Path


class CollectionOperation(ABC):
    """Interface for a fixed-name Mongo collection (source or summary)."""

    @staticmethod
    @abstractmethod
    def create(database: Database) -> None:
        """Create the collection with its schema validator and indexes."""

    @staticmethod
    @abstractmethod
    def delete(database: Database) -> None:
        """Delete every document in the collection and drop it."""

    @staticmethod
    @abstractmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> None:
        """Export every document in the collection to a CSV file."""

    @staticmethod
    @abstractmethod
    def import_data(database: Database, input_path: Path, delimiter: str) -> None:
        """Import the rows of `input_path` into the collection."""
