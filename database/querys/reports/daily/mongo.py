from typing import List
from pandas import DataFrame
from database import (
    TableNameDatabase,
    DailyReportFieldDatabase,
    MongoDatabaseFactory,
    MongoDatabase,
    DailyReportQuery
)
from utils.trasform import DailyReportResponseTrasform
from utils.config import ConfigurationHandler
from utils.log import log


class MongoDailyReportQuery(DailyReportQuery):
    """Mongo query class for daily reports table."""

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
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = MongoDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")

    def new_report(self, data: DataFrame):
        try:
            status_insert = False
            data_json: List[dict] = data.to_dict(orient="records")
            self.__database.open_connection()
            if self.__database.connected:
                if data_json:
                    collection = self.__database.get_cursor(table=TableNameDatabase.DAILY_REPORT)
                    response = collection.insert_many(data_json)
                    status_insert = response.acknowledged
                    self.__database.close_connection()
                else:
                    status_insert = True
            return status_insert
        except Exception as e:
            log.error(f"Failed to insert a daily report. {e}")
            return False
        
    def get_report(self, layer_type: str, date: str):
        try:
            traffic: DataFrame = DataFrame()
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.DAILY_REPORT)
                result = collection.find({
                    DailyReportFieldDatabase.DATE: date,
                    DailyReportFieldDatabase.TYPE_LAYER: layer_type
                })
                if result:
                    data = DailyReportResponseTrasform.default_model_mongo(result)
                    if not data.empty: traffic = data
                self.__database.close_connection()
            return traffic
        except Exception as e:
            log.error(f"Failed to get daily report. {e}")
            return DataFrame()
