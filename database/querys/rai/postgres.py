from typing import List
from database import (
    TableNameDatabase,
    RaiFieldDatabase,
    PostgresDatabaseFactory,
    PostgresDatabase,
    RaiQuery
)
from model import RaiModel
from utils.config import ConfigurationHandler
from utils.trasform import RaiResponseTrasform
from utils.log import log


class PostgresRaiQuery(RaiQuery):
    """Postgres query class for rai table."""

    __database: PostgresDatabase

    def __init__(self):
        try:
            config = ConfigurationHandler()
            factory = PostgresDatabaseFactory()
            database = factory.get_database(uri=config.uri_postgres)
            self.__database = database
        except Exception as e:
            log.error(f"Failed to connect to Postgres database. {e}")


    def set_database(self, uri: str) -> None:
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = PostgresDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log.error(f"Failed to connect to Postgres database. {e}")

    def new_interface(self, new: RaiModel) -> bool:
        try:
            status_insert = False
            self.__database.open_connection()
            if self.__database.connected:
                connection = self.__database.get_connection()
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        INSERT INTO
                            {TableNameDatabase.RAI}
                        (
                            {RaiFieldDatabase.NAME},
                            {RaiFieldDatabase.CAPACITY}
                        )
                        VALUES
                        (%s, %s)
                    """,
                    (new.name, new.capacity)
                )
                status = cursor.statusmessage
                connection.commit()
                if status == "INSERT 0 1": status_insert = True
                self.__database.close_connection()
            return status_insert
        except Exception as e:
            log.error(f"Failed to create new interface. {e}")
            return False

    def get_interface(self, name: str) -> RaiModel | None:
        try:
            interface: RaiModel | None = None
            self.__database.open_connection()
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        SELECT
                            *
                        FROM
                            {TableNameDatabase.RAI}
                        WHERE
                            {RaiFieldDatabase.NAME} = %s
                    """,
                    (name,)
                )
                result = cursor.fetchone()
                if result: 
                    data = RaiResponseTrasform.default_model_postgres([result])
                    if data: interface = data[0]
                self.__database.close_connection()
            return interface
        except Exception as e:
            log.error(f"Failed to get interface. {e}")
            return None

    def get_interfaces(self) -> List[RaiModel]:
        try:
            interfaces: List[RaiModel] = []
            self.__database.open_connection()
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        SELECT 
                            *
                        FROM
                            {TableNameDatabase.RAI}
                    """
                )
                result = cursor.fetchall()
                self.__database.close_connection()
                if result: interfaces = RaiResponseTrasform.default_model_postgres(result)
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces. {e}")
            return []