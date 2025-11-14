from typing import Any
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from scanbackup.constants import (
    TableName,
    BBIPFieldName,
    IPBrasFieldName,
    DailySummaryFieldName,
)
from scanbackup.database.schemas.borde import BORDE_SCHEMA as BORDE_SCHEMA_MONGO
from scanbackup.database.schemas.bras import BRAS_SCHEMA as BRAS_SCHEMA_MONGO
from scanbackup.database.schemas.caching import CACHING_SCHEMA as CACHING_SCHEMA_MONGO
from scanbackup.database.schemas.rai import RAI_SCHEMA as RAI_SCHEMA_MONGO
from scanbackup.database.schemas.ixp import IXP_SCHEMA as IXP_SCHEMA_MONGO
from scanbackup.database.schemas.ipBras import (
    IP_HISTORY_SCHEMA as IP_BRAS_SCHEMA_MONGO,
)
from scanbackup.database.schemas.dailySummary import (
    DAILY_SUMMARY_SCHEMA as DAILY_SUMMARY_SCHEMA_MONGO,
)
from scanbackup.utils import log


class DatabaseMongo:
    _client: MongoClient[Any]
    _name_db: str
    _uri: str
    connected: bool = False

    def __init__(self, uri: str) -> None:
        self._uri = uri
        self.open_connection(uri)

    def _check_collection(self, name: str) -> bool:
        """Check if the collection exists.

        :param name: Collection name
        :type name: str
        :return bool: True if the collection exists, False otherwise.
        """
        db = self._client[self._name_db]
        collection_list = db.list_collection_names()
        return name in collection_list

    def get_uri(self) -> str:
        """Get the URI database.

        :returns str: URI database.
        """
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
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")
            self.connected = False
        else:
            self.connected = True

    def get_connection(self) -> MongoClient[Any]:
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
        self._client.close()
        self.connected = False

    def initialize(self) -> bool:
        """Create all collections and schemas in the database."""
        try:
            self.open_connection(self._uri)
            db = self._client[self._name_db]
            if not self._check_collection(TableName.BORDE):
                db.create_collection(TableName.BORDE, validator=BORDE_SCHEMA_MONGO)
                collection = db[TableName.BORDE]
                collection.create_index(
                    [
                        (BBIPFieldName.NAME, ASCENDING),
                        (BBIPFieldName.TYPE, ASCENDING),
                        (BBIPFieldName.DATE, ASCENDING),
                        (BBIPFieldName.TIME, ASCENDING),
                    ],
                    unique=True,
                    name="unique_borde_index",
                )
                collection.create_index(
                    [(BBIPFieldName.DATE, ASCENDING)], name="borde_by_date_index"
                )
            if not self._check_collection(TableName.BRAS):
                db.create_collection(TableName.BRAS, validator=BRAS_SCHEMA_MONGO)
                collection = db[TableName.BRAS]
                collection.create_index(
                    [
                        (BBIPFieldName.NAME, ASCENDING),
                        (BBIPFieldName.TYPE, ASCENDING),
                        (BBIPFieldName.DATE, ASCENDING),
                        (BBIPFieldName.TIME, ASCENDING),
                    ],
                    unique=True,
                    name="unique_bras_index",
                )
                collection.create_index(
                    [(BBIPFieldName.DATE, ASCENDING)], name="bras_by_date_index"
                )
            if not self._check_collection(TableName.CACHING):
                db.create_collection(TableName.CACHING, validator=CACHING_SCHEMA_MONGO)
                collection = db[TableName.CACHING]
                collection.create_index(
                    [
                        (BBIPFieldName.NAME, ASCENDING),
                        (BBIPFieldName.TYPE, ASCENDING),
                        (BBIPFieldName.DATE, ASCENDING),
                        (BBIPFieldName.TIME, ASCENDING),
                    ],
                    unique=True,
                    name="unique_caching_index",
                )
                collection.create_index(
                    [(BBIPFieldName.DATE, ASCENDING)], name="caching_by_date_index"
                )
            if not self._check_collection(TableName.RAI):
                db.create_collection(TableName.RAI, validator=RAI_SCHEMA_MONGO)
                collection = db[TableName.RAI]
                collection.create_index(
                    [
                        (BBIPFieldName.NAME, ASCENDING),
                        (BBIPFieldName.TYPE, ASCENDING),
                        (BBIPFieldName.DATE, ASCENDING),
                        (BBIPFieldName.TIME, ASCENDING),
                    ],
                    unique=True,
                    name="unique_rai_index",
                )
                collection.create_index(
                    [(BBIPFieldName.DATE, ASCENDING)], name="rai_by_date_index"
                )
            if not self._check_collection(TableName.IXP):
                db.create_collection(TableName.IXP, validator=IXP_SCHEMA_MONGO)
                collection = db[TableName.IXP]
                collection.create_index(
                    [
                        (BBIPFieldName.NAME, ASCENDING),
                        (BBIPFieldName.TYPE, ASCENDING),
                        (BBIPFieldName.DATE, ASCENDING),
                        (BBIPFieldName.TIME, ASCENDING),
                    ],
                    unique=True,
                    name="unique_ixp_index",
                )
                collection.create_index(
                    [(BBIPFieldName.DATE, ASCENDING)], name="ixp_by_date_index"
                )
            if not self._check_collection(TableName.IP_BRAS):
                db.create_collection(
                    TableName.IP_BRAS, validator=IP_BRAS_SCHEMA_MONGO
                )
                collection = db[TableName.IP_BRAS]
                collection.create_index(
                    [
                        (IPBrasFieldName.BRAS_NAME, ASCENDING),
                        (IPBrasFieldName.DATE, ASCENDING),
                        (IPBrasFieldName.TIME, ASCENDING),
                    ],
                    unique=True,
                    name="unique_ip_bras_index",
                )
                collection.create_index(
                    [(IPBrasFieldName.DATE, ASCENDING)],
                    name="ip_bras_by_date_index",
                )
            if not self._check_collection(TableName.DAILY_SUMMARY):
                db.create_collection(
                    TableName.DAILY_SUMMARY, validator=DAILY_SUMMARY_SCHEMA_MONGO
                )
                collection = db[TableName.DAILY_SUMMARY]
                collection.create_index(
                    [
                        (DailySummaryFieldName.NAME, ASCENDING),
                        (DailySummaryFieldName.TYPE_LAYER, ASCENDING),
                        (DailySummaryFieldName.TYPE, ASCENDING),
                        (DailySummaryFieldName.DATE, ASCENDING),
                    ],
                    unique=True,
                    name="unique_daily_summary_index",
                )
                collection.create_index(
                    [(DailySummaryFieldName.DATE, ASCENDING)],
                    name="daily_summary_by_date_index",
                )
                collection.create_index(
                    [
                        (DailySummaryFieldName.DATE, ASCENDING),
                        (DailySummaryFieldName.TYPE_LAYER, ASCENDING),
                    ],
                    name="daily_summary_by_date_typelayer_index",
                )
            self.close_connection()
        except Exception as error:
            log.error(f"Fallo al inicializar la base datos del sistema en MongoDB - {error}")
            return False
        else:
            return True

    def drop(self) -> bool:
        """Deletes all collections in the database."""
        try:
            self.open_connection(self._uri)
            db = self._client[self._name_db]
            borde_collection: Collection[Any] = db[TableName.BORDE]
            borde_collection.delete_many({})
            borde_collection.drop()
            bras_collection: Collection[Any] = db[TableName.BRAS]
            bras_collection.delete_many({})
            bras_collection.drop()
            caching_collection: Collection[Any] = db[TableName.CACHING]
            caching_collection.delete_many({})
            caching_collection.drop()
            rai_collection: Collection[Any] = db[TableName.RAI]
            rai_collection.delete_many({})
            rai_collection.drop()
            ixp_collection: Collection[Any] = db[TableName.IXP]
            ixp_collection.delete_many({})
            ixp_collection.drop()
            ip_history_collection: Collection[Any] = db[TableName.IP_BRAS]
            ip_history_collection.delete_many({})
            ip_history_collection.drop()
            daily_report_collection: Collection[Any] = db[TableName.DAILY_SUMMARY]
            daily_report_collection.delete_many({})
            daily_report_collection.drop()
            self.close_connection()
        except Exception as error:
            log.error(f"Fallo al destruir la base de datos del sistema en MongoDB - {error}")
            return False
        else:
            return True
