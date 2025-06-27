from typing import List
from pandas import DataFrame
from constants import TableName, DailyReportFieldName, header_daily_report
from database.libs.product.mongo import DatabaseMongo
from database.libs.factory.mongo import DatabaseMongoFactory
from database.querys.daily.query import DailyReportQuery
from database.utils.adapter import DailyReportResponseAdapter
from utils.config import ConfigurationHandler
from utils.log import log


class DailyReportMongoQuery(DailyReportQuery):
    """Mongo query class for daily reports table."""

    __database: DatabaseMongo

    def __init__(self, uri: str | None = None):
        try:
            if not uri:
                config = ConfigurationHandler()
                uri = config.uri_mongo
            factory = DatabaseMongoFactory()
            database = factory.get_database(uri=uri)
            self.__database = database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")


    def set_database(self, uri: str):
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = DatabaseMongoFactory().get_database(uri=uri)
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
                    collection = self.__database.get_cursor(table=TableName.DAILY_REPORT)
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
            traffic: DataFrame = DataFrame(columns=header_daily_report)
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableName.DAILY_REPORT)
                result = collection.find({
                    DailyReportFieldName.DATE: date,
                    DailyReportFieldName.TYPE_LAYER: layer_type
                })
                if result:
                    data = DailyReportResponseAdapter.to_dataframe(result)
                    if not data.empty: traffic = data
                self.__database.close_connection()
            return traffic
        except Exception as e:
            log.error(f"Failed to get daily report. {e}")
            return DataFrame(columns=header_daily_report)
