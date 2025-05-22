from io import StringIO
from typing import List
from pandas import DataFrame
from database import (
    TableNameDatabase,
    TrafficHistoryFieldDatabase,
    PostgresDatabaseFactory,
    PostgresDatabase,
    TrafficHistoryQuery
)
from model import TrafficHistoryModel
from utils.trasform import TrafficHistoryResponseTrasform
from utils.config import ConfigurationHandler
from utils.log import log


class PostgresTrafficHistoryQuery(TrafficHistoryQuery):
    """Postgres query class for history traffic table."""

    __instance: "PostgresTrafficHistoryQuery | None" = None
    __database: PostgresDatabase

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(PostgresTrafficHistoryQuery, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        try:
            if not hasattr(self, "__initialized"):
                self.__initialized = True
                config = ConfigurationHandler()
                database = PostgresDatabaseFactory().get_database(uri=config.uri_postgres)
                self.__database = database
        except Exception as e:
            log.error(f"Failed to connect to Postgres database. {e}")

    
    def __create_buffer(self, data: List[TrafficHistoryModel]) -> StringIO:
        """Create buffer to insert data in database."""
        buffer = StringIO()
        for interface in data:
            line = ';'.join(
                'null' if value is None else str(value)
                for value in interface.model_dump().values()
            ) + '\n'
            buffer.write(line)
        buffer.seek(0)
        return buffer

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
            new_database = PostgresDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log.error(f"Failed to connect to Postgres database. {e}")

    def new_traffic(self, traffic: List[TrafficHistoryModel]):
        try:
            self.__database.open_connection()
            if self.__database.connected:
                connection = self.__database.get_connection()
                cursor = self.__database.get_cursor()
                cursor.copy_from(
                    file=self.__create_buffer(traffic),
                    table=TableNameDatabase.TRAFFIC_HISTORY.lower(),
                    sep=';',
                    columns=(
                        TrafficHistoryFieldDatabase.DATE.lower(),
                        TrafficHistoryFieldDatabase.TIME.lower(),
                        TrafficHistoryFieldDatabase.ID_LAYER.lower(),
                        TrafficHistoryFieldDatabase.TYPE_LAYER.lower(),
                        TrafficHistoryFieldDatabase.IN_PROM.lower(),
                        TrafficHistoryFieldDatabase.IN_MAX.lower(),
                        TrafficHistoryFieldDatabase.OUT_PROM.lower(),
                        TrafficHistoryFieldDatabase.OUT_MAX.lower()
                    )
                )
                connection.commit()
                self.__database.close_connection()
        except Exception as e:
            log.error(f"Failed to insert traffic histories. {e}")
            return False
        else:
            return True
        
    def get_traffic(self, date: str, time: str, id_layer: str):
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
                            {TableNameDatabase.TRAFFIC_HISTORY}
                        WHERE
                            {TrafficHistoryFieldDatabase.DATE} = %s
                            AND
                            {TrafficHistoryFieldDatabase.TIME} = %s
                            AND
                            {TrafficHistoryFieldDatabase.ID_LAYER} = %s
                    """,
                    (date, time, id_layer)
                )
                result = cursor.fetchone()
                if result:
                    data = TrafficHistoryResponseTrasform.default_model_postgres([result])
                    if not data.empty: traffic = data
                self.__database.close_connection()
            return traffic
        except Exception as e:
            log.error(f"Failed to get traffic. {e}")
            return DataFrame()

    def get_traffic_layer_by_date(self, layer_type: str, date: str):
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
                            {TableNameDatabase.TRAFFIC_HISTORY}
                        WHERE
                            {TrafficHistoryFieldDatabase.DATE} = %s
                            AND
                            {TrafficHistoryFieldDatabase.TYPE_LAYER} = %s
                    """,
                    (date, layer_type)
                )
                result = cursor.fetchall()
                if result: traffic = TrafficHistoryResponseTrasform.default_model_postgres(result)
            return traffic
        except Exception as e:
            log.error(f"Failed to get traffic. {e}")
            return DataFrame()
