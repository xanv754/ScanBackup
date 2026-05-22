from typing import Any, Dict
from pathlib import Path
from pymongo import MongoClient
from scanbackup.shared import (
    ModuleSystem,
    SchemaDBAvailable,
    Configuration,
    DatabaseConfigModel,
    LayerConfigModel,
    LayerNotDefined,
    MongoDatabaseError,
    MongoConnectionError,
    MongoCollectionNotFoundError,
    MongoCreateCollectionError,
    MongoDeleteCollectionError,
    MongoImportCollectionError,
    MongoExportCollectionError,
    DatabaseDataNotFoundError,
    DatabaseDataContentError,
    FileExtensionError,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
    SuffixCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.collections.records.bbip.traffic import (
    BBIPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.records.bbip.ip import (
    IPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.sources.bbip.bbip import (
    BBIPSourceCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.sources.bbip.ip import (
    IPSourceCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.summaries.bbip.daily_traffic import (
    BBIPDailySummaryCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.summaries.bbip.daily_ip import (
    IPDailySummaryCollection,
)


class MongoDatabase:
    _instance: "MongoDatabase | None" = None
    _config: DatabaseConfigModel
    _client: MongoClient[Any]
    _uri: str
    connected: bool = False

    def __new__(cls) -> "MongoDatabase":
        if not cls._instance:
            cls._instance = super(MongoDatabase, cls).__new__(cls)
        return cls._instance

    def _check_collection(self, name: str) -> bool:
        """Check if the collection exists."""
        db = self._client[self._name_db]
        collection_list = db.list_collection_names()
        return name in collection_list

    def set_uri(self, config: DatabaseConfigModel) -> None:
        self._config = config
        self._uri = f"mongodb://{self._config.user}:{self._config.password}@{self._config.host}:{self._config.port}"

    def get_uri(self) -> str:
        """Get the URI database."""
        return self._uri

    def open_connection(self) -> None:
        """Open a connection to the database.

        :param uri: URI database
        :type uri: str
        """
        try:
            if not self.connected:
                self._client = MongoClient(self._uri)
        except Exception as error:
            self.connected = False
            raise MongoConnectionError(error=error, extra_msg="Fallo al abrir conexión")
        else:
            self.connected = True

    def get_connection(self) -> MongoClient[Dict[str, Any]]:
        """Get a connection to the database.

        :return MongoClient[Any]: Client of MongoDB
        """
        return self._client

    def close_connection(self) -> None:
        """Close the connection to the database."""
        try:
            self._client.close()
            self.connected = False
        except Exception as error:
            raise MongoConnectionError(
                error=error, extra_msg="Fallo al cerrar conexión"
            )

    def create_collections(self, config: LayerConfigModel) -> None:
        """Create all collections and schemas in the database."""
        try:
            self.open_connection(self._uri)
            db = self._client[self._config.name]

            if not self._check_collection(MongoCollectionName.BBIP_SOURCES):
                BBIPSourceCollection.create(database=db)

            layers_bbip = config.bbip.names
            for layer in layers_bbip:
                layer = layer.upper()
                name_collection = layer + "_" + SuffixCollectionName.BBIP_HISTORIES
                if not self._check_collection(name_collection):
                    BBIPCollection.create(name_collection=name_collection, database=db)

            if not self._check_collection(MongoCollectionName.BBIP_DAILY_SUMMARY):
                BBIPDailySummaryCollection.create(database=db)

            if not self._check_collection(name_collection):
                IPSourceCollection.create(name_collection=name_collection, database=db)

            layers_ip = config.ip.names
            for layer in layers_ip:
                layer = layer.upper()
                name_collection = layer + "_" + SuffixCollectionName.IP_HISTORIES
                if not self._check_collection(MongoCollectionName.IP_BRAS):
                    IPCollection.create(name_collection=name_collection, database=db)

            if not self._check_collection(MongoCollectionName.IP_DAILY_SUMMARY):
                IPDailySummaryCollection.create(database=db)

            self.close_connection()
        except MongoCreateCollectionError:
            raise
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al crear colecciones"
            )

    def import_data(
        self,
        name_collection: str,
        config: LayerConfigModel,
        filepath: str,
        delimiter: str | None = None,
    ) -> None:
        filepath = Path(filepath)
        try:
            if not filepath.exists():
                raise DatabaseDataNotFoundError()

            if not self._check_collection(name_collection):
                raise MongoCollectionNotFoundError(name_collection)

            if filepath.suffix != ".csv" or filepath.suffix != ".txt":
                raise FileExtensionError(filepath=filepath, module=ModuleSystem.MONGO)

            if name_collection in config.bbip.names:
                BBIPCollection.import_data(
                    name_collection=name_collection,
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection is config.ip.names:
                IPCollection.import_data(
                    name_collection=name_collection,
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.BBIP_SOURCES:
                BBIPSourceCollection.import_data(
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.IP_SOURCES:
                IPSourceCollection.import_data(
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.BBIP_DAILY_SUMMARY:
                BBIPDailySummaryCollection.import_data(
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.IP_DAILY_SUMMARY:
                IPDailySummaryCollection.import_data(
                    database=self._client,
                    input_path=filepath,
                    delimiter=delimiter,
                )
            else:
                raise LayerNotDefined(layer_name=name_collection)
        except LayerNotDefined:
            raise
        except FileExtensionError:
            raise
        except MongoCollectionNotFoundError:
            raise
        except MongoImportCollectionError:
            raise
        except DatabaseDataContentError:
            raise
        except DatabaseDataNotFoundError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al importar la data"
            )

    def export_data(
        self,
        config: LayerConfigModel,
        name_collection: str,
        dirpath: str | None = None,
        delimiter: str | None = None,
        include_id: bool = True,
    ) -> None:
        if not dirpath:
            dirpath = Path.home()
        else:
            dirpath = Path(dirpath)
        try:
            if name_collection and self._check_collection(name_collection):
                raise MongoCollectionNotFoundError(name_collection)

            if name_collection is config.bbip.names:
                BBIPCollection.export_data(
                    name_collection=name_collection,
                    database=self._client,
                    output_path=Path(dirpath / f"{name_collection}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )

            elif name_collection is config.ip.names:
                IPCollection.export_data(
                    name_collection=name_collection,
                    database=self._client,
                    output_path=Path(dirpath / f"{name_collection}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            elif name_collection == MongoCollectionName.BBIP_SOURCES:
                BBIPSourceCollection.export_data(
                    database=self._client,
                    output_path=Path(
                        dirpath / f"{MongoCollectionName.BBIP_SOURCES}.csv"
                    ),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            elif name_collection == MongoCollectionName.IP_SOURCES:
                IPSourceCollection.export_data(
                    database=self._client,
                    output_path=Path(dirpath / f"{MongoCollectionName.IP_SOURCES}.csv"),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            elif name_collection == MongoCollectionName.BBIP_DAILY_SUMMARY:
                BBIPDailySummaryCollection.export_data(
                    database=self._client,
                    output_path=Path(
                        dirpath / f"{MongoCollectionName.BBIP_DAILY_SUMMARY}.csv"
                    ),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            elif name_collection == MongoCollectionName.IP_DAILY_SUMMARY:
                IPDailySummaryCollection.export_data(
                    database=self._client,
                    output_path=Path(
                        dirpath / f"{MongoCollectionName.IP_DAILY_SUMMARY}.csv"
                    ),
                    delimiter=delimiter,
                    include_id=include_id,
                )
            else:
                raise LayerNotDefined(layer_name=name_collection)
        except LayerNotDefined:
            raise
        except MongoCollectionNotFoundError:
            raise
        except MongoExportCollectionError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al importar la data"
            )

    def drop(self, config: LayerConfigModel, force: bool = False) -> None:
        """Deletes all collections in the database."""
        try:
            self.open_connection(self._uri)
            db = self._client[self._config.name]

            for layer in config.bbip.names:
                layer = layer.upper() + "_" + SuffixCollectionName.BBIP_HISTORIES
                if not self._check_collection(layer):
                    continue
                if not force:
                    self.export_data(config, layer)
                BBIPCollection.delete(name_collection=layer, database=db)

            if self._check_collection(MongoCollectionName.BBIP_DAILY_SUMMARY):
                if not force:
                    self.export_data(config, MongoCollectionName.BBIP_DAILY_SUMMARY)
                BBIPDailySummaryCollection.delete(db)

            if self._check_collection(MongoCollectionName.BBIP_SOURCES):
                if not force:
                    self.export_data(config, MongoCollectionName.BBIP_SOURCES)
                BBIPSourceCollection.delete(db)

            for layer in config.bbip.names:
                layer = layer.upper() + "_" + SuffixCollectionName.IP_HISTORIES
                if not self._check_collection(layer):
                    continue
                if not force:
                    self.export_data(config, layer)
                IPCollection.delete(name_collection=layer, database=db)

            if self._check_collection(MongoCollectionName.IP_DAILY_SUMMARY):
                if not force:
                    self.export_data(config, MongoCollectionName.IP_DAILY_SUMMARY)
                IPDailySummaryCollection.delete(db)

            if self._check_collection(MongoCollectionName.IP_SOURCES):
                if not force:
                    self.export_data(config, MongoCollectionName.IP_SOURCES)
                IPSourceCollection.delete(db)

            self.close_connection()
        except MongoExportCollectionError:
            raise
        except MongoDeleteCollectionError:
            raise
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al eliminar colecciones"
            )
