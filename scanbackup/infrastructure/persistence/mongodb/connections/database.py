from typing import Any, Dict
from pymongo import MongoClient
from pymongo.collection import Collection
from shared import (
    MongoConnectionError,
    MongoDatabaseError,
    MongoCreateCollectionError,
    MongoDeleteCollectionError,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
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


class DatabaseMongo:
    _client: MongoClient[Any]
    _name_db: str
    _uri: str
    connected: bool = False

    def __init__(self, uri: str) -> None:
        self._uri = uri
        self.open_connection(uri)

    def _check_collection(self, name: str) -> bool:
        """Check if the collection exists."""
        db = self._client[self._name_db]
        collection_list = db.list_collection_names()
        return name in collection_list

    def get_uri(self) -> str:
        """Get the URI database."""
        return self._uri

    def open_connection(self, uri: str | None = None) -> None:
        """Open a connection to the database.

        :param uri: URI database
        :type uri: str
        """
        try:
            if not self.connected:
                if not uri:
                    uri = self._uri
                name_db = uri.split("/")[-1]
                self._name_db = name_db
                self._client = MongoClient(uri)
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

    def get_cursor(self, table: str | None = None) -> Collection[Any]:
        """Get a cursor to the database.

        :param table: Collection name
        :type table: str | None
        :return MongoClient[Any]: Connection in the database collection
        """
        if table:
            return self._client[self._name_db][table]
        else:
            return self._client[self._name_db].get_default_collection()

    def close_connection(self) -> None:
        """Close the connection to the database."""
        try:
            self._client.close()
            self.connected = False
        except Exception as error:
            raise MongoConnectionError(
                error=error, extra_msg="Fallo al cerrar conexión"
            )

    def initialize(self) -> bool:
        """Create all collections and schemas in the database."""
        try:
            self.open_connection(self._uri)
            db = self._client[self._name_db]
            if not self._check_collection(MongoCollectionName.BBIP_SOURCES):
                BBIPSourceCollection.create(database=db)
            if not self._check_collection(MongoCollectionName.BORDE):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.BORDE, database=db
                )
            if not self._check_collection(MongoCollectionName.BRAS):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.BRAS, database=db
                )
            if not self._check_collection(MongoCollectionName.CACHING):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.CACHING, database=db
                )
            if not self._check_collection(MongoCollectionName.RAI):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.RAI, database=db
                )
            if not self._check_collection(MongoCollectionName.IXP):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.IXP, database=db
                )
            if not self._check_collection(MongoCollectionName.DINT):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.DINT, database=db
                )
            if not self._check_collection(MongoCollectionName.DIST):
                BBIPCollection.create(
                    name_collection=MongoCollectionName.DIST, database=db
                )
            if not self._check_collection(MongoCollectionName.BBIP_DAILY_SUMMARY):
                BBIPDailySummaryCollection.create(database=db)
            if not self._check_collection(MongoCollectionName.IP_SOURCES):
                IPSourceCollection.create(database=db)

            if not self._check_collection(MongoCollectionName.IP_BRAS):
                IPCollection.create(
                    name_collection=MongoCollectionName.IP_BRAS, database=db
                )
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

    def drop(self) -> None:
        """Deletes all collections in the database."""
        try:
            self.open_connection(self._uri)
            db = self._client[self._name_db]
            self.close_connection()
        except MongoDeleteCollectionError:
            raise
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoDatabaseError(
                error=error, message="Error inesperado al eliminar colecciones"
            )
