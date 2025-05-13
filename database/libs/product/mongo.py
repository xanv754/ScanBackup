from pymongo import MongoClient
from pymongo.collection import Collection
from database import (
    TableNameDatabase,
    Database,
    BORDE_SCHEMA_MONGO,
    BRAS_SCHEMA_MONGO,
    CACHING_SCHEMA_MONGO,
    RAI_SCHEMA_MONGO,
    TRAFFIC_HISTORY_SCHEMA_MONGO,
    IP_HISTORY_SCHEMA_MONGO
)
from utils import log

class MongoDatabase(Database):
    __client: MongoClient
    __connection: MongoClient
    __uri: str
    connected: bool = False

    def __init__(self, uri: str) -> "MongoDatabase":
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

    def migration(self) -> bool:
        try:
            self.open_connection()
            if not self.__check_collection(TableNameDatabase.BORDE):
                self.__connection.create_collection(
                    TableNameDatabase.BORDE,
                    validator=BORDE_SCHEMA_MONGO
                )
            if not self.__check_collection(TableNameDatabase.BRAS):
                self.__connection.create_collection(
                    TableNameDatabase.BRAS,
                    validator=BRAS_SCHEMA_MONGO
                )
            if not self.__check_collection(TableNameDatabase.CACHING):
                self.__connection.create_collection(
                    TableNameDatabase.CACHING,
                    validator=CACHING_SCHEMA_MONGO
                )
            if not self.__check_collection(TableNameDatabase.RAI):
                self.__connection.create_collection(
                    TableNameDatabase.RAI,
                    validator=RAI_SCHEMA_MONGO
                )
            if not self.__check_collection(TableNameDatabase.TRAFFIC_HISTORY):
                self.__connection.create_collection(
                    TableNameDatabase.TRAFFIC_HISTORY,
                    validator=TRAFFIC_HISTORY_SCHEMA_MONGO
                )
            if not self.__check_collection(TableNameDatabase.IP_HISTORY):
                self.__connection.create_collection(
                    TableNameDatabase.IP_HISTORY,
                    validator=IP_HISTORY_SCHEMA_MONGO
                )
            self.close_connection()
        except Exception as e:
            log.error(f"Failed to migrate MongoDB database. {e}")
            return False
        else:
            return True

    def rollback(self) -> bool:
        try:
            self.open_connection()
            borde_collection: Collection = self.__connection[TableNameDatabase.BORDE]
            borde_collection.delete_many({})
            borde_collection.drop()
            bras_collection: Collection = self.__connection[TableNameDatabase.BRAS]
            bras_collection.delete_many({})
            bras_collection.drop()
            caching_collection: Collection = self.__connection[TableNameDatabase.CACHING]
            caching_collection.delete_many({})
            caching_collection.drop()
            rai_collection: Collection = self.__connection[TableNameDatabase.RAI]
            rai_collection.delete_many({})
            rai_collection.drop()
            traffic_history_collection: Collection = self.__connection[TableNameDatabase.TRAFFIC_HISTORY]
            traffic_history_collection.delete_many({})
            traffic_history_collection.drop()
            ip_history_collection: Collection = self.__connection[TableNameDatabase.IP_HISTORY]
            ip_history_collection.delete_many({})
            ip_history_collection.drop()
            self.close_connection()
        except Exception as e:
            log.error(f"Failed to rollback MongoDB database. {e}")
            return False
        else:
            return True
