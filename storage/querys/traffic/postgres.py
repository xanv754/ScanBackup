from typing import List
from model.trafficHistory import TrafficHistoryModel
from storage.constant.tables import TableNameDatabase
from storage.constant.fields import TrafficHistoryFieldDatabase
from storage.database.factory.postgres import PostgresDatabaseFactory
from storage.database.product.postgres import PostgresDatabase
from storage.querys.traffic.traffic import TrafficHistoryQuery
from utils.config import ConfigurationHandler
from utils.trasform import TrafficHistoryResponseTrasform
from utils.log import LogHandler


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
            LogHandler.log(f"Failed to connect to Postgres database. {e}", path=__file__, err=True)

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
            LogHandler.log(f"Failed to connect to Postgres database. {e}", path=__file__, err=True)

    def new_traffic(self, traffic: List[TrafficHistoryModel]) -> bool:
        try:
            if self.__database.connected:
                connection = self.__database.get_connection()
                cursor = self.__database.get_cursor()
                total_insert = 0
                total_inserted = 0
                for history in traffic:
                    if not self.get_traffic(date=history.date, time=history.time, id_layer=history.idLayer):
                        total_insert += 1
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
                        status = cursor.statusmessage
                        connection.commit()
                        if status == "INSERT 0 1": total_inserted += 1
                self.__database.close_connection()
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to insert traffic histories. {e}", path=__file__, err=True)
            return False
        else:
            return total_inserted == total_insert

    def get_traffic(self, date: str, time: str, id_layer: str) -> TrafficHistoryModel | None:
        try:
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        SELECT
                            *
                        FROM
                            traffic_history
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
                    if data: return data[0]
                return None
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to get traffic. {e}", path=__file__, err=True)
            return None

    # def get_all_traffic_by_layer(self, layer_name: str) -> List[TrafficHistoryModel]:
    #     try:
    #         result: List[TrafficHistoryModel] = []
    #         if self.__database.connected:
    #             collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
    #             cursor = collection.find({TrafficHistoryFieldDatabase.TYPE_LAYER: layer_name})
    #             for data in cursor:
    #                 result.append(
    #                     TrafficHistoryModel(
    #                         date=data[TrafficHistoryFieldDatabase.DATE],
    #                         time=data[TrafficHistoryFieldDatabase.TIME],
    #                         idLayer=data[TrafficHistoryFieldDatabase.ID_LAYER],
    #                         typeLayer=data[TrafficHistoryFieldDatabase.TYPE_LAYER],
    #                         inProm=data[TrafficHistoryFieldDatabase.IN_PROM],
    #                         inMax=data[TrafficHistoryFieldDatabase.IN_MAX],
    #                         outProm=data[TrafficHistoryFieldDatabase.OUT_PROM],
    #                         outMax=data[TrafficHistoryFieldDatabase.OUT_MAX],
    #                     )
    #                 )
    #             self.__database.close_connection()
    #         return result
    #     except Exception as e:
    #         LogHandler.log(f"Failed to get all traffic of {layer_name} layer. {e}", path=__file__, err=True)
    #         return []

    # def get_all_traffic_by_id(self, id: str) -> List[TrafficHistoryModel]:
    #     try:
    #         result: List[TrafficHistoryModel] = []
    #         if self.__database.connected:
    #             collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
    #             cursor = collection.find({TrafficHistoryFieldDatabase.ID_LAYER: id})
    #             for data in cursor:
    #                 result.append(
    #                     TrafficHistoryModel(
    #                         date=data[TrafficHistoryFieldDatabase.DATE],
    #                         time=data[TrafficHistoryFieldDatabase.TIME],
    #                         idLayer=data[TrafficHistoryFieldDatabase.ID_LAYER],
    #                         typeLayer=data[TrafficHistoryFieldDatabase.TYPE_LAYER],
    #                         inProm=data[TrafficHistoryFieldDatabase.IN_PROM],
    #                         inMax=data[TrafficHistoryFieldDatabase.IN_MAX],
    #                         outProm=data[TrafficHistoryFieldDatabase.OUT_PROM],
    #                         outMax=data[TrafficHistoryFieldDatabase.OUT_MAX],
    #                     )
    #                 )
    #             self.__database.close_connection()
    #         return result
    #     except Exception as e:
    #         LogHandler.log(f"Failed to get all traffic of {id}. {e}", path=__file__, err=True)
    #         return []

    # def get_all_traffic_by_date(self, date: str) -> List[TrafficHistoryModel]:
    #     try:
    #         result: List[TrafficHistoryModel] = []
    #         if self.__database.connected:
    #             collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
    #             cursor = collection.find({TrafficHistoryFieldDatabase.DATE: date})
    #             for data in cursor:
    #                 result.append(
    #                     TrafficHistoryModel(
    #                         date=data[TrafficHistoryFieldDatabase.DATE],
    #                         time=data[TrafficHistoryFieldDatabase.TIME],
    #                         idLayer=data[TrafficHistoryFieldDatabase.ID_LAYER],
    #                         typeLayer=data[TrafficHistoryFieldDatabase.TYPE_LAYER],
    #                         inProm=data[TrafficHistoryFieldDatabase.IN_PROM],
    #                         inMax=data[TrafficHistoryFieldDatabase.IN_MAX],
    #                         outProm=data[TrafficHistoryFieldDatabase.OUT_PROM],
    #                         outMax=data[TrafficHistoryFieldDatabase.OUT_MAX],
    #                     )
    #                 )
    #             self.__database.close_connection()
    #         return result
    #     except Exception as e:
    #         LogHandler.log(f"Failed to get all traffic of date {date}. {e}", path=__file__, err=True)
    #         return []

    # def get_all_traffic_date_by_layer(self, layer_name: str, date: str) -> List[TrafficHistoryModel]:
    #     try:
    #         result: List[TrafficHistoryModel] = []
    #         if self.__database.connected:
    #             collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
    #             cursor = collection.find(
    #                 {
    #                     TrafficHistoryFieldDatabase.DATE: date,
    #                     TrafficHistoryFieldDatabase.TYPE_LAYER: layer_name
    #                 }
    #             )
    #             for data in cursor:
    #                 result.append(
    #                     TrafficHistoryModel(
    #                         date=data[TrafficHistoryFieldDatabase.DATE],
    #                         time=data[TrafficHistoryFieldDatabase.TIME],
    #                         idLayer=data[TrafficHistoryFieldDatabase.ID_LAYER],
    #                         typeLayer=data[TrafficHistoryFieldDatabase.TYPE_LAYER],
    #                         inProm=data[TrafficHistoryFieldDatabase.IN_PROM],
    #                         inMax=data[TrafficHistoryFieldDatabase.IN_MAX],
    #                         outProm=data[TrafficHistoryFieldDatabase.OUT_PROM],
    #                         outMax=data[TrafficHistoryFieldDatabase.OUT_MAX],
    #                     )
    #                 )
    #             self.__database.close_connection()
    #         return result
    #     except Exception as e:
    #         LogHandler.log(f"Failed to get all traffic of date {date} in the {layer_name} layer. {e}", path=__file__, err=True)
    #         return []

    # def get_all_traffic_date_by_id(self, id: str, date: str) -> List[TrafficHistoryModel]:
    #     try:
    #         result: List[TrafficHistoryModel] = []
    #         if self.__database.connected:
    #             collection = self.__database.get_cursor(table=TableNameDatabase.TRAFFIC_HISTORY)
    #             cursor = collection.find(
    #                 {
    #                     TrafficHistoryFieldDatabase.DATE: date,
    #                     TrafficHistoryFieldDatabase.ID_LAYER: id
    #                 }
    #             )
    #             for data in cursor:
    #                 result.append(
    #                     TrafficHistoryModel(
    #                         date=data[TrafficHistoryFieldDatabase.DATE],
    #                         time=data[TrafficHistoryFieldDatabase.TIME],
    #                         idLayer=data[TrafficHistoryFieldDatabase.ID_LAYER],
    #                         typeLayer=data[TrafficHistoryFieldDatabase.TYPE_LAYER],
    #                         inProm=data[TrafficHistoryFieldDatabase.IN_PROM],
    #                         inMax=data[TrafficHistoryFieldDatabase.IN_MAX],
    #                         outProm=data[TrafficHistoryFieldDatabase.OUT_PROM],
    #                         outMax=data[TrafficHistoryFieldDatabase.OUT_MAX],
    #                     )
    #                 )
    #             self.__database.close_connection()
    #         return result
    #     except Exception as e:
    #         LogHandler.log(f"Failed to get all traffic of date {date} in {id}. {e}", path=__file__, err=True)
    #         return []
