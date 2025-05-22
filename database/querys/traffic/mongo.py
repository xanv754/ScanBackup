from typing import List
from database import (
    TableNameDatabase,
    TrafficHistoryFieldDatabase,
    MongoDatabaseFactory,
    MongoDatabase,
    TrafficHistoryQuery
)
from model import TrafficHistoryModel
from utils.trasform import TrafficHistoryResponseTrasform
from utils.config import ConfigurationHandler
from utils.log import log


class MongoTrafficHistoryQuery(TrafficHistoryQuery):
    """Mongo query class for history traffic table."""

    __database: MongoDatabase

    def __init__(self):
        try:
            config = ConfigurationHandler()
            factory = MongoDatabaseFactory()
            database = factory.get_database(uri=config.uri_mongo)
            self.__database = database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")


    def set_database(self, uri: str):
        """Set the connection database.

        Parameters
        ----------
        uri : str
            New URI to connection database.
        """
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = MongoDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")

    def new_traffic(self, traffic: List[TrafficHistoryModel]):
        try:
            status_insert = False
            traffic_json: List[dict] = []
            traffic_json = [data.model_dump() for data in traffic]
            self.__database.open_connection()
            if self.__database.connected:
                if traffic_json:
                    collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                    response = collection.insert_many(traffic_json)
                    status_insert = response.acknowledged
                    self.__database.close_connection()
                else:
                    log.warning(f"Traffic histories of {traffic[0].typeLayer} to insert is empty.")
                    status_insert = True
            return status_insert
        except Exception as e:
            log.error(f"Failed to insert histories traffic. {e}")
            return False
        
    def get_traffic(self, date: str, time: str, id_layer: str):
        try:
            traffic: TrafficHistoryModel | None = None
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                result = collection.find_one({
                    TrafficHistoryFieldDatabase.DATE: date,
                    TrafficHistoryFieldDatabase.TIME: time,
                    TrafficHistoryFieldDatabase.ID_LAYER: id_layer
                })
                if result:
                    data = TrafficHistoryResponseTrasform.default_model_mongo([result])
                    if data: traffic = data[0]
                self.__database.close_connection()
            return traffic
        except Exception as e:
            log.error(f"Failed to get traffic. {e}")
            return None
        
    def get_traffic_layer_by_date(self, layer_type: str, date: str):
        try:
            traffic: List[TrafficHistoryModel] = []
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                cursor = collection.find({
                    TrafficHistoryFieldDatabase.DATE: date,
                    TrafficHistoryFieldDatabase.TYPE_LAYER: layer_type
                })
                if cursor: traffic = TrafficHistoryResponseTrasform.default_model_mongo(cursor)
                self.__database.close_connection()
            return traffic
        except Exception as e:
            log.error(f"Failed to get traffic. {e}")
            return []