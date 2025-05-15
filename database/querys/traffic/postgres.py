from typing import List
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

    def __new__(cls) -> "PostgresTrafficHistoryQuery":
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
            new_database = PostgresDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log.error(f"Failed to connect to Postgres database. {e}")

    def new_traffic(self, traffic: List[TrafficHistoryModel]) -> bool:
        try:
            self.__database.open_connection()
            if self.__database.connected:
                connection = self.__database.get_connection()
                cursor = self.__database.get_cursor()
                for history in traffic:
                    cursor.execute(
                        f"""
                            INSERT INTO
                                {TableNameDatabase.TRAFFIC_HISTORY}
                            (
                                {TrafficHistoryFieldDatabase.DATE},
                                {TrafficHistoryFieldDatabase.TIME},
                                {TrafficHistoryFieldDatabase.ID_LAYER},
                                {TrafficHistoryFieldDatabase.TYPE_LAYER},
                                {TrafficHistoryFieldDatabase.IN_PROM},
                                {TrafficHistoryFieldDatabase.IN_MAX},
                                {TrafficHistoryFieldDatabase.OUT_PROM},
                                {TrafficHistoryFieldDatabase.OUT_MAX}
                            )
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            history.date,
                            history.time,
                            history.idLayer,
                            history.typeLayer,
                            history.inProm,
                            history.inMax,
                            history.outProm,
                            history.outMax
                        )
                    )
                    connection.commit()
                self.__database.close_connection()
        except Exception as e:
            log.error(f"Failed to insert traffic histories. {e}")
            return False
        else:
            return True
        
    def get_traffic(self, date: str, time: str, id_layer: str) -> TrafficHistoryModel | None:
        try:
            traffic: TrafficHistoryModel | None = None
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
                    if data: traffic = data[0]
                self.__database.close_connection()
            return traffic
        except Exception as e:
            log.error(f"Failed to get traffic. {e}")
            return None

    def get_traffic_layer_by_date(self, layer_type: str, date: str) -> List[TrafficHistoryModel]:
        try:
            traffic: List[TrafficHistoryModel] = []
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
            return []
