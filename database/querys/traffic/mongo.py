from ast import Eq
from typing import List
from model.trafficHistory import TrafficHistoryModel
from database.constant.tables import TableNameDatabase
from database.constant.fields import TrafficHistoryFieldDatabase
from database.libs.factory.mongo import MongoDatabaseFactory
from database.libs.product.mongo import MongoDatabase
from database.querys.traffic.traffic import TrafficHistoryQuery
from utils.config import ConfigurationHandler
from utils.trasform import TrafficHistoryResponseTrasform
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


    def set_database(self, uri: str) -> None:
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

    def new_traffic(self, traffic: List[TrafficHistoryModel]) -> bool:
        try:
            self.open_connection()
            if self.__database.connected:
                traffic_json: List[dict] = []
                for data in traffic:
                    if not self.get_traffic(date=data.date, time=data.time, id_layer=data.idLayer):
                        traffic_json.append(data.model_dump())
                if traffic_json:
                    collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                    response = collection.insert_many(traffic_json)
                    self.__database.close_connection()
                    return response.acknowledged
                return False
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            log.error(f"Failed to insert histories traffic. {e}")
            return False

    # def get_traffic(self, date: str, time: str, id_layer: str) -> TrafficHistoryModel | None:
    #     try:
    #         self.open_connection()
    #         if self.__database.connected:
    #             collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
    #             response = collection.find_one(
    #                 {
    #                     TrafficHistoryFieldDatabase.DATE: date,
    #                     TrafficHistoryFieldDatabase.TIME: time,
    #                     TrafficHistoryFieldDatabase.ID_LAYER: id_layer
    #                 }
    #             )
    #             self.__database.close_connection()
    #             if response:
    #                 data = TrafficHistoryResponseTrasform.default_model_mongo([response])
    #                 if data: return data[0]
    #             return None
    #         else:
    #             raise Exception("Database not connected.")
    #     except Exception as e:
    #         log.error(f"Failed to get traffic. {e}")
    #         return None

    # def get_traffic_interface_by_date(self, id: str, date: str) -> List[TrafficHistoryModel]:
    #     try:
    #         self.open_connection()
    #         if self.__database.connected:
    #             collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
    #             cursor = collection.find(
    #                 {
    #                     TrafficHistoryFieldDatabase.DATE: date,
    #                     TrafficHistoryFieldDatabase.ID_LAYER: id
    #                 }
    #             )
    #             result: List[TrafficHistoryModel] = []
    #             self.__database.close_connection()
    #             if cursor:
    #                 result = TrafficHistoryResponseTrasform.default_model_mongo(cursor)
    #             return result
    #         else:
    #             raise Exception("Database not connected.")
    #     except Exception as e:
    #         log.error(f"Failed to get traffic. {e}")
    #         return []
        
    def get_traffic_layer_by_date(self, layer_type: str, date: str) -> List[TrafficHistoryModel]:
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
        
    # def get_traffic_by_date(self, date: str) -> List[TrafficHistoryModel]:
    #     try:
    #         self.open_connection()
    #         if self.__database.connected:
    #             collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
    #             cursor = collection.find(
    #                 {
    #                     TrafficHistoryFieldDatabase.DATE: date
    #                 }
    #             )
    #             result: List[TrafficHistoryModel] = []
    #             self.__database.close_connection()
    #             if cursor:
    #                 result = TrafficHistoryResponseTrasform.default_model_mongo(cursor)
    #             return result
    #         else:
    #             raise Exception("Database not connected.")
    #     except Exception as e:
    #         log.error(f"Failed to get traffic. {e}")
    #         return []
        
    # def get_traffic_layer_by_month(self, layer_type: str, month: str) -> List[TrafficHistoryModel]:
    #     try:
    #         self.open_connection()
    #         if self.__database.connected:
    #             collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
    #             cursor = collection.find(
    #                 {
    #                     "$expr": {
    #                         "$eq": [
    #                             {"$month": "$date"},
    #                             month
    #                         ]
    #                     },
    #                     TrafficHistoryFieldDatabase.TYPE_LAYER: layer_type
    #                 }
    #             )
    #             result: List[TrafficHistoryModel] = []
    #             self.__database.close_connection()
    #             if cursor:
    #                 result = TrafficHistoryResponseTrasform.default_model_mongo(cursor)
    #             return result
    #         else:
    #             raise Exception("Database not connected.")
    #     except Exception as e:
    #         log.error(f"Failed to get traffic. {e}")
    #         return []