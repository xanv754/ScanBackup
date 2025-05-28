from io import StringIO
from typing import List
from pandas import DataFrame
from database import (
    TableNameDatabase,
    DailyReportFieldDatabase,
    PostgresDatabaseFactory,
    PostgresDatabase,
    DailyReportQuery
)
from utils.trasform import DailyReportResponseTrasform
from utils.config import ConfigurationHandler
from utils.log import log


class PostgresDailyReportQuery(DailyReportQuery):
    """Postgres query class for history traffic table."""

    __database: PostgresDatabase

    def __init__(self):
        try:
            config = ConfigurationHandler()
            factory = PostgresDatabaseFactory()
            database = factory.get_database(uri=config.uri_postgres)
            self.__database = database
        except Exception as e:
            log.error(f"Failed to connect to Postgres database. {e}")

    
    def __create_buffer(self, df: DataFrame) -> StringIO:
        """Create buffer to insert data in database."""
        buffer = StringIO()
        df.to_csv(buffer, sep=';', header=False, index=False)
        buffer.seek(0)
        return buffer

    def set_database(self, uri: str):
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = PostgresDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log.error(f"Failed to connect to Postgres database. {e}")

    def new_report(self, data: DataFrame):
        try:
            self.__database.open_connection()
            if self.__database.connected:
                connection = self.__database.get_connection()
                cursor = self.__database.get_cursor()
                cursor.copy_from(
                    file=self.__create_buffer(data),
                    table=TableNameDatabase.DAILY_REPORT.lower(),
                    sep=';',
                    columns=(
                        DailyReportFieldDatabase.DATE.lower(),
                        DailyReportFieldDatabase.ID_LAYER.lower(),
                        DailyReportFieldDatabase.TYPE_LAYER.lower(),
                        DailyReportFieldDatabase.IN_PROM.lower(),
                        DailyReportFieldDatabase.IN_MAX.lower(),
                        DailyReportFieldDatabase.OUT_PROM.lower(),
                        DailyReportFieldDatabase.OUT_MAX.lower()
                    )
                )
                connection.commit()
                self.__database.close_connection()
        except Exception as e:
            log.error(f"Failed to insert a daily report. {e}")
            return False
        else:
            return True
        
    def get_report(self, layer_type: str, date: str):
        try:
            traffic: DataFrame = DataFrame()
            self.__database.open_connection()
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        SELECT
                            *
                        FROM
                            {TableNameDatabase.DAILY_REPORT}
                        WHERE
                            {DailyReportFieldDatabase.DATE} = %s
                            AND
                            {DailyReportFieldDatabase.TYPE_LAYER} = %s
                    """,
                    (date, layer_type)
                )
                result = cursor.fetchall()
                if result: traffic = DailyReportResponseTrasform.default_model_postgres(result)
            return traffic
        except Exception as e:
            log.error(f"Failed to get daily report. {e}")
            return DataFrame()

