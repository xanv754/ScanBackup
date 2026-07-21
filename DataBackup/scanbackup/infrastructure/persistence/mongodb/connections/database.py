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
    TrafficHistoryBBIPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.history import (
    IPHistoryBBIPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.traffic.source import (
    TrafficSourceBBIPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.source import (
    IPSourceBBIPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.traffic.summaries.daily import (
    TrafficDailySummaryBBIPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.summaries.daily import (
    IPDailySummaryBBIPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.traffic.summaries.hour import (
    TrafficHourSummaryBBIPCollection,
)
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.summaries.hour import (
    IPHourSummaryBBIPCollection,
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

    def _match_history_layer(
        self, name_collection: str, layer_names: list[str], suffix: str
    ) -> bool:
        """Check whether `name_collection` is the history collection of one of `layer_names`.

        History collections are named "<LAYER>_<suffix>" (e.g. "BORDE_TRAFFIC_HISTORY_BBIP"),
        not the bare layer name, so a plain membership check against `layer_names` never matches.
        """
        expected_suffix = "_" + suffix
        upper_name = name_collection.upper()
        if not upper_name.endswith(expected_suffix):
            return False
        layer_prefix = upper_name[: -len(expected_suffix)]
        return layer_prefix in {layer.upper() for layer in layer_names}

    def _fixed_collections(self) -> dict[str, type]:
        """Map every fixed-name collection to its handler class."""
        return {
            MongoCollectionName.TRAFFIC_SOURCES.value: TrafficSourceBBIPCollection,
            MongoCollectionName.IP_SOURCES.value: IPSourceBBIPCollection,
            MongoCollectionName.TRAFFIC_DAILY_SUMMARY.value: TrafficDailySummaryBBIPCollection,
            MongoCollectionName.IP_DAILY_SUMMARY.value: IPDailySummaryBBIPCollection,
            MongoCollectionName.TRAFFIC_HOUR_SUMMARY.value: TrafficHourSummaryBBIPCollection,
            MongoCollectionName.IP_HOUR_SUMMARY.value: IPHourSummaryBBIPCollection,
        }

    def _create_missing_layer_collections(
        self,
        database: Any,
        layer_names: list[str],
        suffix: str,
        collection_cls: type,
    ) -> None:
        """Create the per-layer history collection for every layer not already present."""
        for layer in layer_names:
            name_collection = f"{layer.upper()}_{suffix}"
            if not self._check_collection(name_collection):
                collection_cls.create(name_collection=name_collection, database=database)

    def set_uri(self, config: DatabaseConfigModel) -> None:
        """Set the database configuration and build its connection URI."""
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
        """List every collection currently present in the database."""
        self.open_connection()
        return self._client[self._config.name].list_collection_names()

    def create_collections(self, config: LayerConfigModel) -> None:
        """Create all collections and schemas in the database."""
        try:
            self.open_connection()
            db = self._client[self._config.name]

            for name, collection_cls in self._fixed_collections().items():
                if not self._check_collection(name):
                    collection_cls.create(database=db)

            self._create_missing_layer_collections(
                db,
                config.bbip.names,
                SuffixCollectionName.TRAFFIC_HISTORIES.value,
                TrafficHistoryBBIPCollection,
            )
            self._create_missing_layer_collections(
                db,
                config.ip.names,
                SuffixCollectionName.IP_HISTORIES.value,
                IPHistoryBBIPCollection,
            )
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
        input_filepath: str,
        delimiter: str,
    ) -> None:
        """Import `input_filepath` into `name_collection`, routing by collection type."""
        try:
            filepath = Path(input_filepath)
            if not filepath.exists():
                raise FileImportNotFoundError(input_filepath)
            if filepath.suffix != ".csv" and filepath.suffix != ".txt":
                raise FileExtensionError(filepath=str(filepath.resolve()))

            self.open_connection()
            if not self._check_collection(name_collection):
                raise MongoCollectionNotFoundError(name_collection)
            database = self._client[self._config.name]
            fixed_collections = self._fixed_collections()

            if self._match_history_layer(
                name_collection, config.bbip.names, SuffixCollectionName.TRAFFIC_HISTORIES.value
            ):
                TrafficHistoryBBIPCollection.import_data(
                    name_collection=name_collection,
                    database=database,
                    input_path=filepath,
                    delimiter=delimiter,
                )

            elif self._match_history_layer(
                name_collection, config.ip.names, SuffixCollectionName.IP_HISTORIES.value
            ):
                IPHistoryBBIPCollection.import_data(
                    name_collection=name_collection,
                    database=database,
                    input_path=filepath,
                    delimiter=delimiter,
                )

            elif name_collection in fixed_collections:
                fixed_collections[name_collection].import_data(
                    database=database,
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
        dirpath: Path | None = None,
        include_id: bool = True,
    ) -> str:
        """Export `name_collection` to CSV, routing by collection type."""
        try:
            self.open_connection()

            if not self._check_collection(name_collection):
                raise MongoCollectionNotFoundError(name_collection)
            database = self._client[self._config.name]
            fixed_collections = self._fixed_collections()

            if self._match_history_layer(
                name_collection, config.bbip.names, SuffixCollectionName.TRAFFIC_HISTORIES.value
            ):
                filepath = TrafficHistoryBBIPCollection.export_data(
                    name_collection=name_collection,
                    database=database,
                    dirpath=dirpath,
                    include_id=include_id,
                )

            elif self._match_history_layer(
                name_collection, config.ip.names, SuffixCollectionName.IP_HISTORIES.value
            ):
                filepath = IPHistoryBBIPCollection.export_data(
                    name_collection=name_collection,
                    database=database,
                    dirpath=dirpath,
                    include_id=include_id,
                )

            elif name_collection in fixed_collections:
                filepath = fixed_collections[name_collection].export_data(
                    database=database,
                    dirpath=dirpath,
                    include_id=include_id,
                )

            else:
                raise LayerNotDefined(layer_name=name_collection)

            return filepath
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
        finally:
            self.close_connection()
