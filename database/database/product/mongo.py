from pymongo import MongoClient
from pymongo.collection import Collection
from database.constant.tables import TableNameDatabase
from database.database.product.database import Database
from database.schemas.mongo.borde import BORDE_SCHEMA
from database.schemas.mongo.bras import BRAS_SCHEMA
from database.schemas.mongo.caching import CACHING_SCHEMA
from database.schemas.mongo.rai import RAI_SCHEMA
from database.schemas.mongo.trafficHistory import TRAFFIC_HISTORY_SCHEMA
from database.schemas.mongo.ipHistory import IP_HISTORY_SCHEMA
from utils.log import LogHandler

class MongoDatabase(Database):
    __client: MongoClient
    __connection: MongoClient
    connected: bool = False

    def __init__(self, uri: str) -> "MongoDatabase":
        try:
            self.__client = MongoClient(uri)
            name_db = uri.split("/")[-1]
            self.__connection = self.__client[name_db]
        except Exception as e:
            LogHandler.log(f"Failed to connect to MongoDB database. {e}", path=__file__, err=True)
        else:
            self.connected = True

    def get_connection(self) -> MongoClient:
        return self.__connection

    def get_cursor(self, table: str | None = None) -> Collection:
        if table:
            return self.__connection[table]
        else:
            return self.__connection.get_default_collection()

    def close_connection(self) -> None:
        self.__client.close()
        self.connected = False

    def migration(self) -> bool:
        try:
            self.__connection.create_collection(
                TableNameDatabase.BORDE,
                validator=BORDE_SCHEMA
            )
            self.__connection.create_collection(
                TableNameDatabase.BRAS,
                validator=BRAS_SCHEMA
            )
            self.__connection.create_collection(
                TableNameDatabase.CACHING,
                validator=CACHING_SCHEMA
            )
            self.__connection.create_collection(
                TableNameDatabase.RAI,
                validator=RAI_SCHEMA
            )
            self.__connection.create_collection(
                TableNameDatabase.TRAFFIC_HISTORY,
                validator=TRAFFIC_HISTORY_SCHEMA
            )
            self.__connection.create_collection(
                TableNameDatabase.IP_HISTORY,
                validator=IP_HISTORY_SCHEMA
            )
        except Exception as e:
            LogHandler.log(f"Failed to migrate MongoDB database. {e}", path=__file__, err=True)
            return False
        else:
            return True

    def rollback(self) -> bool:
        try:
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
        except Exception as e:
            LogHandler.log(f"Failed to rollback MongoDB database. {e}", path=__file__, err=True)
            return False
        else:
            return True
