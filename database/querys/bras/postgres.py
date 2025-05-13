from typing import List
from database import (
    TableNameDatabase,
    BrasFieldDatabase,
    PostgresDatabaseFactory,
    PostgresDatabase,
    BrasQuery
)
from model import BrasModel
from utils.config import ConfigurationHandler
from utils.trasform import BrasResponseTrasform
from utils.log import log


class PostgresBrasQuery(BrasQuery):
    """Postgres query class for bras table."""

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

    def new_interface(self, new: BrasModel) -> bool:
        try:
            status_insert = False
            self.__database.open_connection()
            if self.__database.connected:
                connection = self.__database.get_connection()
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        INSERT INTO
                            {TableNameDatabase.BRAS}
                        (
                            {BrasFieldDatabase.NAME},
                            {BrasFieldDatabase.TYPE},
                            {BrasFieldDatabase.CAPACITY}
                        )
                        VALUES
                        (%s, %s, %s)
                    """,
                    (new.name, new.type, new.capacity)
                )
                status = cursor.statusmessage
                connection.commit()
                if status == "INSERT 0 1": status_insert = True
                self.__database.close_connection()
            return status_insert
        except Exception as e:
            log.error(f"Failed to create new bras. {e}")
            return False

    def get_interface(self, brasname: str, type: str) -> BrasModel | None:
        try:
            interface: BrasModel | None = None
            self.__database.open_connection()
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        SELECT
                            *
                        FROM
                            {TableNameDatabase.BRAS}
                        WHERE
                            {BrasFieldDatabase.NAME} = %s
                            AND
                            {BrasFieldDatabase.TYPE} = %s
                    """,
                    (brasname, type)
                )
                result = cursor.fetchone()
                if result: 
                    data = BrasResponseTrasform.default_model_postgres([result])
                    if data: interface = data[0]
                self.__database.close_connection()
            return interface
        except Exception as e:
            log.error(f"Failed to get bras. {e}")
            return None

    def get_interfaces(self) -> List[BrasModel]:
        try:
            interfaces: List[BrasModel] = []
            self.__database.open_connection()
            if self.__database.connected:
                cursor = self.__database.get_cursor()
                cursor.execute(
                    f"""
                        SELECT
                            *
                        FROM
                            {TableNameDatabase.BRAS}
                    """
                )
                result = cursor.fetchall()
                if result: interfaces = BrasResponseTrasform.default_model_postgres(result)
                self.__database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get bras. {e}")
            return []