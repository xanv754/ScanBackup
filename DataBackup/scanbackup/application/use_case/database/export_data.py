from pathlib import Path
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.shared import DatabaseConfigModel, LayerConfigModel


class DatabaseExportUseCase:
    """Exports a named collection of the database into a .csv file."""

    _database: MongoDatabase

    def __init__(self, database: MongoDatabase) -> None:
        """Store the database gateway used to export the data.

        Args:
            database (MongoDatabase): Gateway used to connect and export data.
        """
        self._database = database

    def execute(
        self,
        cfg_db: DatabaseConfigModel,
        cfg_layers: LayerConfigModel,
        name_collection: str,
        dirpath: Path,
        include_id: bool,
    ) -> str:
        """Export `name_collection` to CSV, routing by collection type.

        Args:
            cfg_db (DatabaseConfigModel): Connection settings used to reach the database.
            cfg_layers (LayerConfigModel): Configured layers, used to route the
                target collection to its handler.
            name_collection (str): Name of the collection to export.
            dirpath (Path): Directory where the resulting .csv file is written.
            include_id (bool): Whether to include the MongoDB '_id' in the export.

        Returns:
            str: The absolute path of the generated .csv file.
        """
        self._database.set_uri(cfg_db)
        return self._database.export_data(
            config=cfg_layers,
            name_collection=name_collection,
            dirpath=dirpath,
            include_id=include_id,
        )
