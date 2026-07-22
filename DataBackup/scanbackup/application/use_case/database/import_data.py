from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.shared import DatabaseConfigModel, LayerConfigModel


class DatabaseImportUseCase:
    """Imports a .csv file into a named collection of the database."""

    _database: MongoDatabase

    def __init__(self, database: MongoDatabase) -> None:
        """Store the database gateway used to import the data.

        Args:
            database (MongoDatabase): Gateway used to connect and import data.
        """
        self._database = database

    def execute(
        self,
        cfg_db: DatabaseConfigModel,
        cfg_layers: LayerConfigModel,
        name_collection: str,
        input_filepath: str,
        delimiter: str,
    ) -> None:
        """Import `input_filepath` into `name_collection`, routing by collection type.

        Args:
            cfg_db (DatabaseConfigModel): Connection settings used to reach the database.
            cfg_layers (LayerConfigModel): Configured layers, used to route the
                target collection to its handler.
            name_collection (str): Name of the collection to import into.
            input_filepath (str): Path of the .csv file to import.
            delimiter (str): Field delimiter used in the .csv file.
        """
        self._database.set_uri(cfg_db)
        self._database.import_data(
            name_collection=name_collection,
            config=cfg_layers,
            input_filepath=input_filepath,
            delimiter=delimiter,
        )
