from scanbackup.domain import BaseDatabase
from scanbackup.shared import DatabaseConfigModel


class DatabaseInspectUseCase:
    """Lists every collection currently present in the database."""

    _database: BaseDatabase

    def __init__(self, database: BaseDatabase) -> None:
        """Store the database gateway used to inspect the collections.

        Args:
            database (BaseDatabase): Gateway used to connect and list collections.
        """
        self._database = database

    def execute(self, cfg_db: DatabaseConfigModel) -> list[str]:
        """List every collection currently present in the database.

        Args:
            cfg_db (DatabaseConfigModel): Connection settings used to reach the database.

        Returns:
            list[str]: Every collection name currently present in the database.
        """
        self._database.set_uri(cfg_db)
        return self._database.get_collection_names()
