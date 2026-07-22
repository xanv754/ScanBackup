from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.shared import DatabaseConfigModel, LayerConfigModel


class DatabaseSetupUseCase:
    """Creates every collection and schema declared in the system configuration."""

    _database: MongoDatabase

    def __init__(self, database: MongoDatabase) -> None:
        """Store the database gateway used to create the collections.

        Args:
            database (MongoDatabase): Gateway used to connect and create collections.
        """
        self._database = database

    def execute(self, cfg_db: DatabaseConfigModel, cfg_layers: LayerConfigModel) -> None:
        """Create every fixed and per-layer collection missing from the database.

        Args:
            cfg_db (DatabaseConfigModel): Connection settings used to reach the database.
            cfg_layers (LayerConfigModel): Configured layers, used to derive the
                per-layer history collections to create.
        """
        self._database.set_uri(cfg_db)
        self._database.create_collections(config=cfg_layers)
