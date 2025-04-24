from database.constant.tables import TableNameDatabase
from database.constant.fields import RaiFieldDatabase
from database.libs.factory.postgres import PostgresDatabaseFactory
from database.libs.product.postgres import PostgresDatabase
from database.querys.rai.rai import RaiQuery
from model.rai import RaiModel
from utils.config import ConfigurationHandler
from utils.trasform import RaiResponseTrasform
from utils.log import LogHandler


class PostgresRaiQuery(RaiQuery):
    """Postgres query class for rai table."""

    __instance: "PostgresRaiQuery | None" = None
    __database: PostgresDatabase

    def __new__(cls) -> "PostgresRaiQuery":
        if not cls.__instance:
            cls.__instance = super(PostgresRaiQuery, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        try:
            if not hasattr(self, "__initialized"):
                self.__initialized = True
                config = ConfigurationHandler()
                database = PostgresDatabaseFactory().get_database(uri=config.uri_postgres)
                self.__database = database
        except Exception as e:
            log = LogHandler()
            log.export(f"Failed to connect to Postgres database. {e}", path=__file__, err=True)

    def set_database(self, uri: str) -> None:
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = PostgresDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log = LogHandler()
            log.export(f"Failed to connect to Postgres database. {e}", path=__file__, err=True)

    def close_connection(self) -> None:
        self.__database.close_connection()

    def new_interface(self, new: RaiModel) -> bool:
        try:
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
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            log = LogHandler()
            log.export(f"Failed to create new interface. {e}", path=__file__, err=True)
            return False
        else:
            return status == "INSERT 0 1"

    def get_interface(self, name: str) -> RaiModel | None:
        try:
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
                    if data: return data[0]
                return None
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            log = LogHandler()
            log.export(f"Failed to get interface. {e}", path=__file__, err=True)
            return None
