from typing import List
from storage.constant.tables import TableNameDatabase
from storage.constant.fields import BordeFieldDatabase
from storage.database.factory.postgres import PostgresDatabaseFactory
from storage.database.product.postgres import PostgresDatabase
from storage.querys.borde.borde import BordeQuery
from model.boder import BordeModel
from utils.config import ConfigurationHandler
from utils.trasform import BordeResponseTrasform
from utils.log import LogHandler


class PostgresBordeQuery(BordeQuery):
    """Mongo query class for borde table."""

    __instance: "PostgresBordeQuery | None" = None
    __database: PostgresDatabase

    def __new__(cls) -> "PostgresBordeQuery":
        if not cls.__instance:
            cls.__instance = super(PostgresBordeQuery, cls).__new__(cls)
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
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = PostgresDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            LogHandler.log(f"Failed to connect to Postgres database. {e}", path=__file__, err=True)

    def close_connection(self) -> None:
        self.__database.close_connection()

    def new_interface(self, new: BordeModel) -> bool:
        try:
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
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to create new interface. {e}", path=__file__, err=True)
            return False
        else:
            return status == "INSERT 0 1"

    def get_interface(self, name: str) -> BordeModel | None:
        try:
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
                    if data: return data[0]
                return None
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to get interface. {e}", path=__file__, err=True)
            return None
        
    def get_interfaces(self) -> List[BordeModel]:
        try:
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
                result: List[BordeModel] = BordeResponseTrasform.default_model_postgres(cursor)
        except Exception as e:
            LogHandler.log(f"Failed to get all interfaces. {e}", path=__file__, err=True)
            return []
        else:
            return result
