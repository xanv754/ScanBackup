from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from systemgrd.constants import TableName, BBIPFieldName, IPBrasHistoryFieldName, DailyReportFieldName
from systemgrd.database.libs.product.database import Database
from systemgrd.database.schemas.borde import BORDE_SCHEMA as BORDE_SCHEMA_MONGO
from systemgrd.database.schemas.bras import BRAS_SCHEMA as BRAS_SCHEMA_MONGO
from systemgrd.database.schemas.caching import CACHING_SCHEMA as CACHING_SCHEMA_MONGO
from systemgrd.database.schemas.rai import RAI_SCHEMA as RAI_SCHEMA_MONGO
from systemgrd.database.schemas.ixp import IXP_SCHEMA as IXP_SCHEMA_MONGO
from systemgrd.database.schemas.ipHistory import IP_HISTORY_SCHEMA as IP_HISTORY_SCHEMA_MONGO
from systemgrd.database.schemas.dailyReport import DAILY_REPORT_SCHEMA as DAILY_REPORT_SCHEMA_MONGO
from systemgrd.utils import log


class DatabaseMongo(Database):
    __client: MongoClient
    __connection: MongoClient
    __uri: str
    connected: bool = False

    def __init__(self, uri: str) -> None:
        self.__uri = uri

    def __check_collection(self, name: str) -> bool:
        """Check if the collection exists."""
        collection_list = self.__connection.list_collection_names()
        return name in collection_list
    
    def open_connection(self) -> None:
        try:
            self.__client = MongoClient(self.__uri)
            name_db = self.__uri.split("/")[-1]
            self.__connection = self.__client[name_db]
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")
            self.connected = False
        else:
            self.connected = True

    def get_connection(self) -> MongoClient:
        return self.__connection

    def get_cursor(self, table: str | None = None) -> Collection:
        if table: return self.__connection[table]
        else: return self.__connection.get_default_collection()

    def close_connection(self) -> None:
        self.__client.close()
        self.connected = False

    def initialize(self) -> bool:
        try:
            self.open_connection()
            if not self.__check_collection(TableName.BORDE):
                self.__connection.create_collection(
                    TableName.BORDE,
                    validator=BORDE_SCHEMA_MONGO
                )
                collection = self.__connection[TableName.BORDE]
                collection.create_index(
                    [
                        (BBIPFieldName.NAME, ASCENDING),
                        (BBIPFieldName.TYPE, ASCENDING),
                        (BBIPFieldName.DATE, ASCENDING),
                        (BBIPFieldName.TIME, ASCENDING)
                    ],
                    unique=True,
                    name="unique_borde_index"
                )
                collection.create_index(
                    [
                        (BBIPFieldName.DATE, ASCENDING)
                    ],
                    name="borde_by_date_index"
                )
            if not self.__check_collection(TableName.BRAS):
                self.__connection.create_collection(
                    TableName.BRAS,
                    validator=BRAS_SCHEMA_MONGO
                )
                collection = self.__connection[TableName.BRAS]
                collection.create_index(
                    [
                        (BBIPFieldName.NAME, ASCENDING),
                        (BBIPFieldName.TYPE, ASCENDING),
                        (BBIPFieldName.DATE, ASCENDING),
                        (BBIPFieldName.TIME, ASCENDING)
                    ],
                    unique=True,
                    name="unique_bras_index"
                )
                collection.create_index(
                    [
                        (BBIPFieldName.DATE, ASCENDING)
                    ],
                    name="bras_by_date_index"
                )
            if not self.__check_collection(TableName.CACHING):
                self.__connection.create_collection(
                    TableName.CACHING,
                    validator=CACHING_SCHEMA_MONGO
                )
                collection = self.__connection[TableName.CACHING]
                collection.create_index(
                    [
                        (BBIPFieldName.NAME, ASCENDING),
                        (BBIPFieldName.TYPE, ASCENDING),
                        (BBIPFieldName.DATE, ASCENDING),
                        (BBIPFieldName.TIME, ASCENDING)
                    ],
                    unique=True,
                    name="unique_caching_index"
                )
                collection.create_index(
                    [
                        (BBIPFieldName.DATE, ASCENDING)
                    ],
                    name="caching_by_date_index"
                )
            if not self.__check_collection(TableName.RAI):
                self.__connection.create_collection(
                    TableName.RAI,
                    validator=RAI_SCHEMA_MONGO
                )
                collection = self.__connection[TableName.RAI]
                collection.create_index(
                    [
                        (BBIPFieldName.NAME, ASCENDING),
                        (BBIPFieldName.TYPE, ASCENDING),
                        (BBIPFieldName.DATE, ASCENDING),
                        (BBIPFieldName.TIME, ASCENDING)
                    ],
                    unique=True,
                    name="unique_rai_index"
                )
                collection.create_index(
                    [
                        (BBIPFieldName.DATE, ASCENDING)
                    ],
                    name="rai_by_date_index"
                )
            if not self.__check_collection(TableName.IXP):
                self.__connection.create_collection(
                    TableName.IXP,
                    validator=IXP_SCHEMA_MONGO
                )
                collection = self.__connection[TableName.IXP]
                collection.create_index(
                    [
                        (BBIPFieldName.NAME, ASCENDING),
                        (BBIPFieldName.TYPE, ASCENDING),
                        (BBIPFieldName.DATE, ASCENDING),
                        (BBIPFieldName.TIME, ASCENDING)
                    ],
                    unique=True,
                    name="unique_ixp_index"
                )
                collection.create_index(
                    [
                        (BBIPFieldName.DATE, ASCENDING)
                    ],
                    name="ixp_by_date_index"
                )
            if not self.__check_collection(TableName.IP_BRAS_HISTORY):
                self.__connection.create_collection(
                    TableName.IP_BRAS_HISTORY,
                    validator=IP_HISTORY_SCHEMA_MONGO
                )
                collection = self.__connection[TableName.IP_BRAS_HISTORY]
                collection.create_index(
                    [
                        (IPBrasHistoryFieldName.BRAS_NAME, ASCENDING),
                        (IPBrasHistoryFieldName.DATE, ASCENDING),
                        (IPBrasHistoryFieldName.TIME, ASCENDING)
                    ],
                    unique=True,
                    name="unique_ip_history_index"
                )
                collection.create_index(
                    [
                        (IPBrasHistoryFieldName.DATE, ASCENDING)
                    ],
                    name="ip_bras_by_date_index"
                )
            if not self.__check_collection(TableName.DAILY_REPORT):
                self.__connection.create_collection(
                    TableName.DAILY_REPORT,
                    validator=DAILY_REPORT_SCHEMA_MONGO
                )
                collection = self.__connection[TableName.DAILY_REPORT]
                collection.create_index(
                    [
                        (DailyReportFieldName.NAME, ASCENDING),
                        (DailyReportFieldName.TYPE_LAYER, ASCENDING),
                        (DailyReportFieldName.TYPE, ASCENDING),
                        (DailyReportFieldName.DATE, ASCENDING)
                    ],
                    unique=True,
                    name="unique_daily_report_index"
                )
                collection.create_index(
                    [
                        (DailyReportFieldName.DATE, ASCENDING)
                    ],
                    name="daily_report_by_date_index"
                )
                collection.create_index(
                    [
                        (DailyReportFieldName.DATE, ASCENDING),
                        (DailyReportFieldName.TYPE_LAYER, ASCENDING)
                    ],
                    name="daily_report_by_date_typelayer_index"
                )
            self.close_connection()
        except Exception as e:
            log.error(f"Failed to migrate MongoDB database. {e}")
            return False
        else:
            return True

    def drop(self) -> bool:
        try:
            self.open_connection()
            borde_collection: Collection = self.__connection[TableName.BORDE]
            borde_collection.delete_many({})
            borde_collection.drop()
            bras_collection: Collection = self.__connection[TableName.BRAS]
            bras_collection.delete_many({})
            bras_collection.drop()
            caching_collection: Collection = self.__connection[TableName.CACHING]
            caching_collection.delete_many({})
            caching_collection.drop()
            rai_collection: Collection = self.__connection[TableName.RAI]
            rai_collection.delete_many({})
            rai_collection.drop()
            ixp_collection: Collection = self.__connection[TableName.IXP]
            ixp_collection.delete_many({})
            ixp_collection.drop()
            ip_history_collection: Collection = self.__connection[TableName.IP_BRAS_HISTORY]
            ip_history_collection.delete_many({})
            ip_history_collection.drop()
            daily_report_collection: Collection = self.__connection[TableName.DAILY_REPORT]
            daily_report_collection.delete_many({})
            daily_report_collection.drop()
            self.close_connection()
        except Exception as e:
            log.error(f"Failed to rollback MongoDB database. {e}")
            return False
        else:
            return True
