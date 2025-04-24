from database.constant.tables import TableNameDatabase
from database.constant.fields import BrasFieldDatabase
from database.database.factory.postgres import PostgresDatabaseFactory
from database.database.product.postgres import PostgresDatabase
from database.querys.bras.bras import BrasQuery
from model.bras import BrasModel
from utils.config import ConfigurationHandler
from utils.trasform import BrasResponseTrasform
from utils.log import LogHandler


class PostgresBrasQuery(BrasQuery):
    """Postgres query class for bras table."""

    __instance: "PostgresBrasQuery | None" = None
    __database: PostgresDatabase

    def __new__(cls) -> "PostgresBrasQuery":
        if not cls.__instance:
            cls.__instance = super(PostgresBrasQuery, cls).__new__(cls)
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

    def new_bras(self, new: BrasModel) -> bool:
        try:
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
                self.__database.close_connection()
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to create new bras. {e}", path=__file__, err=True)
            return False
        else:
            return status == "INSERT 0 1"

    def get_bras(self, brasname: str, type: str) -> BrasModel | None:
        try:
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
                self.__database.close_connection()
                if result: 
                    data = BrasResponseTrasform.default_model_postgres([result])
                    if data: return data[0]
                return None
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to get bras. {e}", path=__file__, err=True)
            return None
