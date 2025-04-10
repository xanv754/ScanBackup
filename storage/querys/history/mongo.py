from typing import List
from model.trafficHistory import TrafficHistoryModel
from storage.constant.tables import TableNameDatabase
from storage.constant.fields import TrafficHistoryFieldDatabase
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
            LogHandler.log(f"Failed to connect to MongoDB database. {e}", path=__file__, err=True)

    def new_histories(self, new_histories: List[TrafficHistoryModel]) -> bool:
        try:
            if self.__database.connected:
                traffic_json: List[dict] = []
                for traffic in new_histories:
                    traffic_json.append(traffic.model_dump())
                collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                response = collection.insert_many(traffic_json)
                self.__database.close_connection()
                return response.acknowledged
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to insert histories traffic. {e}", path=__file__, err=True)
            return False
        
    def get_all_traffic_by_layer(self, layer_name: str) -> List[TrafficHistoryModel]:
        try:
            result: List[TrafficHistoryModel] = []
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                cursor = collection.find({TrafficHistoryFieldDatabase.TYPE_LAYER: layer_name})
                for data in cursor:
                    result.append(
                        TrafficHistoryModel(
                            date=data[TrafficHistoryFieldDatabase.DATE],
                            time=data[TrafficHistoryFieldDatabase.TIME],
                            idLayer=data[TrafficHistoryFieldDatabase.ID_LAYER],
                            typeLayer=data[TrafficHistoryFieldDatabase.TYPE_LAYER],
                            inProm=data[TrafficHistoryFieldDatabase.IN_PROM],
                            inMax=data[TrafficHistoryFieldDatabase.IN_MAX],
                            outProm=data[TrafficHistoryFieldDatabase.OUT_PROM],
                            outMax=data[TrafficHistoryFieldDatabase.OUT_MAX],
                        )
                    )
                self.__database.close_connection()
            return result
        except Exception as e:
            LogHandler.log(f"Failed to get all traffic of {layer_name} layer. {e}", path=__file__, err=True)
            return []
        
    def get_all_traffic_by_id(self, id: str) -> List[TrafficHistoryModel]:
        try:
            result: List[TrafficHistoryModel] = []
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                cursor = collection.find({TrafficHistoryFieldDatabase.ID_LAYER: id})
                for data in cursor:
                    result.append(
                        TrafficHistoryModel(
                            date=data[TrafficHistoryFieldDatabase.DATE],
                            time=data[TrafficHistoryFieldDatabase.TIME],
                            idLayer=data[TrafficHistoryFieldDatabase.ID_LAYER],
                            typeLayer=data[TrafficHistoryFieldDatabase.TYPE_LAYER],
                            inProm=data[TrafficHistoryFieldDatabase.IN_PROM],
                            inMax=data[TrafficHistoryFieldDatabase.IN_MAX],
                            outProm=data[TrafficHistoryFieldDatabase.OUT_PROM],
                            outMax=data[TrafficHistoryFieldDatabase.OUT_MAX],
                        )
                    )
                self.__database.close_connection()
            return result
        except Exception as e:
            LogHandler.log(f"Failed to get all traffic of {id}. {e}", path=__file__, err=True)
            return []
        
    def get_all_traffic_by_date(self, date: str) -> List[TrafficHistoryModel]:
        try:
            result: List[TrafficHistoryModel] = []
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                cursor = collection.find({TrafficHistoryFieldDatabase.DATE: date})
                for data in cursor:
                    result.append(
                        TrafficHistoryModel(
                            date=data[TrafficHistoryFieldDatabase.DATE],
                            time=data[TrafficHistoryFieldDatabase.TIME],
                            idLayer=data[TrafficHistoryFieldDatabase.ID_LAYER],
                            typeLayer=data[TrafficHistoryFieldDatabase.TYPE_LAYER],
                            inProm=data[TrafficHistoryFieldDatabase.IN_PROM],
                            inMax=data[TrafficHistoryFieldDatabase.IN_MAX],
                            outProm=data[TrafficHistoryFieldDatabase.OUT_PROM],
                            outMax=data[TrafficHistoryFieldDatabase.OUT_MAX],
                        )
                    )
                self.__database.close_connection()
            return result
        except Exception as e:
            LogHandler.log(f"Failed to get all traffic of date {date}. {e}", path=__file__, err=True)
            return []
        
    def get_all_traffic_date_by_layer(self, layer_name: str, date: str) -> List[TrafficHistoryModel]:
        try:
            result: List[TrafficHistoryModel] = []
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                cursor = collection.find(
                    {
                        TrafficHistoryFieldDatabase.DATE: date,
                        TrafficHistoryFieldDatabase.TYPE_LAYER: layer_name
                    }
                )
                for data in cursor:
                    result.append(
                        TrafficHistoryModel(
                            date=data[TrafficHistoryFieldDatabase.DATE],
                            time=data[TrafficHistoryFieldDatabase.TIME],
                            idLayer=data[TrafficHistoryFieldDatabase.ID_LAYER],
                            typeLayer=data[TrafficHistoryFieldDatabase.TYPE_LAYER],
                            inProm=data[TrafficHistoryFieldDatabase.IN_PROM],
                            inMax=data[TrafficHistoryFieldDatabase.IN_MAX],
                            outProm=data[TrafficHistoryFieldDatabase.OUT_PROM],
                            outMax=data[TrafficHistoryFieldDatabase.OUT_MAX],
                        )
                    )
                self.__database.close_connection()
            return result
        except Exception as e:
            LogHandler.log(f"Failed to get all traffic of date {date} in the {layer_name} layer. {e}", path=__file__, err=True)
            return []
        
    def get_all_traffic_date_by_id(self, id: str, date: str) -> List[TrafficHistoryModel]:
        try:
            result: List[TrafficHistoryModel] = []
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
                cursor = collection.find(
                    {
                        TrafficHistoryFieldDatabase.DATE: date,
                        TrafficHistoryFieldDatabase.ID_LAYER: id
                    }
                )
                for data in cursor:
                    result.append(
                        TrafficHistoryModel(
                            date=data[TrafficHistoryFieldDatabase.DATE],
                            time=data[TrafficHistoryFieldDatabase.TIME],
                            idLayer=data[TrafficHistoryFieldDatabase.ID_LAYER],
                            typeLayer=data[TrafficHistoryFieldDatabase.TYPE_LAYER],
                            inProm=data[TrafficHistoryFieldDatabase.IN_PROM],
                            inMax=data[TrafficHistoryFieldDatabase.IN_MAX],
                            outProm=data[TrafficHistoryFieldDatabase.OUT_PROM],
                            outMax=data[TrafficHistoryFieldDatabase.OUT_MAX],
                        )
                    )
                self.__database.close_connection()
            return result
        except Exception as e:
            LogHandler.log(f"Failed to get all traffic of date {date} in {id}. {e}", path=__file__, err=True)
            return []