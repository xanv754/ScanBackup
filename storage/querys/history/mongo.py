from typing import List
from model.trafficHistory import TrafficHistoryModel
from storage.constant.tables import TableNameDatabase
from storage.database.factory.mongo import MongoDatabaseFactory
from storage.database.product.mongo import MongoDatabase
from storage.querys.history.history import HistoryTrafficQuery
from utils.config import ConfigurationHandler
from utils.log import LogHandler


class MongoHistoryTrafficQuery(HistoryTrafficQuery):
    """Mongo query class for history traffic table."""

    __instance: "MongoHistoryTrafficQuery | None" = None
    __database: MongoDatabase

    def __new__(cls) -> "MongoHistoryTrafficQuery":
        if not cls.__instance:
            cls.__instance = super(MongoHistoryTrafficQuery, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        try:
            if not hasattr(self, "__initialized"):
                self.__initialized = True
                config = ConfigurationHandler()
                database = MongoDatabaseFactory().get_database(uri=config.uri_mongo)
                self.__database = database
        except Exception as e:
            LogHandler.log(f"Failed to connect to MongoDB database. {e}", path=__file__, err=True)

    def new_histories(self, new_histories: List[TrafficHistoryModel]) -> bool:
        try:
            if self.__database.connected:
                traffic_json: List[dict] = []
                for traffic in new_histories:
                    traffic_json.append(traffic.model_dump())
                collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                response = collection.insert_many(traffic_json)
                return response.acknowledged
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to insert histories traffic. {e}", path=__file__, err=True)
            return False