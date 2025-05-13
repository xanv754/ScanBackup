from typing import List
from database import (
    TableNameDatabase,
    CachingFieldDatabase,
    PostgresDatabaseFactory,
    PostgresDatabase,
    CachingQuery
)
from model import CachingModel
from utils import ConfigurationHandler, CachingResponseTrasform, log


class PostgresCachingQuery(CachingQuery):
    """Postgres query class for caching table."""

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

    def new_interface(self, new: CachingModel) -> bool:
        try:
            status_insert = False
            self.__database.open_connection()
            if self.__database.connected:
                connection = self.__database.get_connection()
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        INSERT INTO
                            {TableNameDatabase.CACHING}
                        (
                            {CachingFieldDatabase.NAME},
                            {CachingFieldDatabase.SERVICE},
                            {CachingFieldDatabase.CAPACITY}
                        )
                        VALUES
                        (%s, %s, %s)
                    """,
                    (new.name, new.service, new.capacity)
                )
                status = cursor.statusmessage
                connection.commit()
                self.__database.close_connection()
                if status == "INSERT 0 1": status_insert = True
            return status_insert
        except Exception as e:
            log.error(f"Failed to create new interface. {e}")
            return False

    def get_interface(self, name: str) -> CachingModel | None:
        try:
            interface: CachingModel | None = None
            self.__database.open_connection()
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        SELECT
                            *
                        FROM
                            {TableNameDatabase.CACHING}
                        WHERE
                            {CachingFieldDatabase.NAME} = %s
                    """,
                    (name,)
                )
                result = cursor.fetchone()
                if result: 
                    data = CachingResponseTrasform.default_model_postgres([result])
                    if data: interface = data[0]
                self.__database.close_connection()
            return interface
        except Exception as e:
            log.error(f"Failed to get interface. {e}")
            return None

    def get_interfaces(self) -> List[CachingModel]:
        try:
            interfaces: List[CachingModel] = []
            self.__database.open_connection()
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        SELECT 
                            *
                        FROM
                            {TableNameDatabase.CACHING}
                    """
                )
                result = cursor.fetchall()
                if result: interfaces = CachingResponseTrasform.default_model_postgres(result)
                self.__database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces. {e}")
            return []