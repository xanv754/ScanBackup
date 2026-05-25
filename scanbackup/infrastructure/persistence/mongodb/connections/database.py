from typing import Any
from pathlib import Path
from pymongo import MongoClient
from pymongo.database import Database
from scanbackup.shared import (
    DatabaseConfigModel,
    LayerConfigModel,
    LayerNotDefined,
    MongoDatabaseError,
    MongoConnectionError,
    MongoCollectionNotFoundError,
    MongoCreateCollectionError,
    MongoImportCollectionError,
    MongoExportCollectionError,
    FileImportNotFoundError,
    DataContentError,
    FileExtensionError,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
    SuffixCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.traffic.history import (
    BBIPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.history import (
    IPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.traffic.source import (
    BBIPSourceCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.source import (
    IPSourceCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.traffic.summaries.daily import (
    BBIPDailySummaryCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.summaries.daily import (
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
        db = self._client[self._config.name]
        collection_list = db.list_collection_names()
        return name in collection_list

    def set_uri(self, config: DatabaseConfigModel) -> None:
        self._config = config
        self._uri = f"mongodb://{self._config.user}:{self._config.password}@{self._config.host}:{self._config.port}/{self._config.name}?authSource={self._config.name}"

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
            raise MongoConnectionError(
                error=error, extra_msg="Fallo al abrir conexión con la base de datos"
            )
        else:
            self.connected = True

    def get_connection(self) -> Database:
        """Get a connection to the database.

        :return Database: Connection to database.
        """
        return self._client[self._config.name]

    def close_connection(self) -> None:
        """Close the connection to the database."""
        try:
            if self.connected:
                self._client.close()
                self.connected = False
        except Exception as error:
            raise MongoConnectionError(
                error=error, extra_msg="Fallo al cerrar conexión"
            )

    def get_collection_names(self) -> list[str]:
        self.open_connection()
        return self._client[self._config.name].list_collection_names()

    def create_collections(self, config: LayerConfigModel) -> None:
        """Create all collections and schemas in the database."""
        try:
            self.open_connection()
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
                if not self._check_collection(name_collection):
                    IPCollection.create(name_collection=name_collection, database=db)

            if not self._check_collection(MongoCollectionName.IP_DAILY_SUMMARY):
                IPDailySummaryCollection.create(database=db)
        except MongoCreateCollectionError:
            raise
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al crear colecciones"
            )
        finally:
            self.close_connection()

    def import_data(
        self,
        name_collection: str,
        config: LayerConfigModel,
        filepath: str,
        delimiter: str = ",",
    ) -> None:
        filepath = Path(filepath)
        try:
            self.open_connection()

            if not filepath.exists():
                raise FileImportNotFoundError()

            if not self._check_collection(name_collection):
                raise MongoCollectionNotFoundError(name_collection)

            if filepath.suffix != ".csv" and filepath.suffix != ".txt":
                raise FileExtensionError(filepath=filepath)

            if name_collection in config.bbip.names:
                BBIPCollection.import_data(
                    name_collection=name_collection,
                    database=self._client[self._config.name],
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection in config.ip.names:
                IPCollection.import_data(
                    name_collection=name_collection,
                    database=self._client[self._config.name],
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.BBIP_SOURCES.value:
                BBIPSourceCollection.import_data(
                    database=self._client[self._config.name],
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.IP_SOURCES.value:
                IPSourceCollection.import_data(
                    database=self._client[self._config.name],
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.BBIP_DAILY_SUMMARY.value:
                BBIPDailySummaryCollection.import_data(
                    database=self._client[self._config.name],
                    input_path=filepath,
                    delimiter=delimiter,
                )
            elif name_collection == MongoCollectionName.IP_DAILY_SUMMARY.value:
                IPDailySummaryCollection.import_data(
                    database=self._client[self._config.name],
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
        except DataContentError:
            raise
        except FileImportNotFoundError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al importar la data"
            )
        finally:
            self.close_connection()

    def export_data(
        self,
        config: LayerConfigModel,
        name_collection: str,
        dirpath: str | None = None,
        delimiter: str = ",",
        include_id: bool = True,
    ) -> str:
        if not dirpath:
            dirpath = Path.home()
        else:
            dirpath = Path(dirpath)
        try:
            self.open_connection()

            if not self._check_collection(name_collection):
                raise MongoCollectionNotFoundError(name_collection)

            if name_collection in config.bbip.names:
                filepath = Path(dirpath / f"{name_collection}.csv")
                BBIPCollection.export_data(
                    name_collection=name_collection,
                    database=self._client[self._config.name],
                    output_path=filepath,
                    delimiter=delimiter,
                    include_id=include_id,
                )

            elif name_collection in config.ip.names:
                filepath = Path(dirpath / f"{name_collection}.csv")
                IPCollection.export_data(
                    name_collection=name_collection,
                    database=self._client[self._config.name],
                    output_path=filepath,
                    delimiter=delimiter,
                    include_id=include_id,
                )
            elif name_collection == MongoCollectionName.BBIP_SOURCES.value:
                filepath = Path(
                    dirpath / f"{MongoCollectionName.BBIP_SOURCES.value}.csv"
                )
                BBIPSourceCollection.export_data(
                    database=self._client[self._config.name],
                    output_path=filepath,
                    delimiter=delimiter,
                    include_id=include_id,
                )
            elif name_collection == MongoCollectionName.IP_SOURCES.value:
                filepath = Path(dirpath / f"{MongoCollectionName.IP_SOURCES.value}.csv")
                IPSourceCollection.export_data(
                    database=self._client[self._config.name],
                    output_path=filepath,
                    delimiter=delimiter,
                    include_id=include_id,
                )
            elif name_collection == MongoCollectionName.BBIP_DAILY_SUMMARY.value:
                filepath = Path(
                    dirpath / f"{MongoCollectionName.BBIP_DAILY_SUMMARY.value}.csv"
                )
                BBIPDailySummaryCollection.export_data(
                    database=self._client[self._config.name],
                    output_path=filepath,
                    delimiter=delimiter,
                    include_id=include_id,
                )
            elif name_collection == MongoCollectionName.IP_DAILY_SUMMARY.value:
                filepath = Path(
                    dirpath / f"{MongoCollectionName.IP_DAILY_SUMMARY.value}.csv"
                )
                IPDailySummaryCollection.export_data(
                    database=self._client[self._config.name],
                    output_path=filepath,
                    delimiter=delimiter,
                    include_id=include_id,
                )
            else:
                raise LayerNotDefined(layer_name=name_collection)
        except LayerNotDefined:
            raise
        except MongoConnectionError:
            raise
        except MongoCollectionNotFoundError:
            raise
        except MongoExportCollectionError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al exportar la data"
            )
        else:
            return filepath
        finally:
            self.close_connection()
