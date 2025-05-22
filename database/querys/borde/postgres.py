from typing import List
from database import (
    TableNameDatabase,
    BordeFieldDatabase,
    PostgresDatabaseFactory,
    PostgresDatabase,
    BordeQuery
)
from model import BordeModel
from utils.trasform import BordeResponseTrasform
from utils.config import ConfigurationHandler
from utils.log import log

class PostgresBordeQuery(BordeQuery):
    """Mongo query class for borde table."""

    __database: PostgresDatabase

    def __init__(self):
        try:
            config = ConfigurationHandler()
            factory = PostgresDatabaseFactory()
            database = factory.get_database(uri=config.uri_postgres)
            self.__database = database
        except Exception as e:
            log.error(f"Failed to connect to Postgres database. {e}")


    def set_database(self, uri: str):
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = PostgresDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log.error(f"Failed to connect to Postgres database. {e}")

    def new_interface(self, new: BordeModel):
        try:
            status_insert = False
            self.__database.open_connection()
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        INSERT INTO
                            {TableNameDatabase.BORDE}
                        (
                            {BordeFieldDatabase.NAME},
                            {BordeFieldDatabase.MODEL},
                            {BordeFieldDatabase.CAPACITY}
                        )
                        VALUES
                        (%s, %s, %s)
                    """,
                    (new.name, new.model, new.capacity)
                )
                status = cursor.statusmessage
                connection = self.__database.get_connection()
                connection.commit()
                self.__database.close_connection()
                if status == "INSERT 0 1": status_insert = True
            return status_insert
        except Exception as e:
            log.error(f"Failed to create new interface. {e}")
            return False

    def get_interface(self, name: str):
        try:
            interface: BordeModel | None = None
            self.__database.open_connection()
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        SELECT
                            *
                        FROM
                            {TableNameDatabase.BORDE}
                        WHERE
                            {BordeFieldDatabase.NAME} = %s
                    """,
                    (name,)
                )
                result = cursor.fetchone()
                if result:
                    data = BordeResponseTrasform.default_model_postgres([result])
                    if data: interface = data[0]
                self.__database.close_connection()
            return interface
        except Exception as e:
            log.error(f"Failed to get interface. {e}")
            return None
        
    def get_interfaces(self):
        try:
            interfaces: List[BordeModel] = []
            self.__database.open_connection()
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        SELECT
                            *
                        FROM
                            {TableNameDatabase.BORDE}
                    """
                )
                interfaces = BordeResponseTrasform.default_model_postgres(cursor)
                self.__database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces. {e}")
            return []
