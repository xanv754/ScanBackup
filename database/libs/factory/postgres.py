from database.libs.factory.database import DatabaseFactory
from database.libs.product.postgres import PostgresDatabase
from utils.log import LogHandler


class PostgresDatabaseFactory(DatabaseFactory):
    """Postgres database factory class."""

    __instance: "PostgresDatabaseFactory | None" = None
    __database: PostgresDatabase | None = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(PostgresDatabaseFactory, cls).__new__(cls)
        return cls.__instance

    def get_database(self, uri: str) -> PostgresDatabase:
        try:
            if not self.__database or (self.__database and not self.__database.connected):
                self.__database = PostgresDatabase(uri=uri)
            return self.__database
        except Exception as e:
            log = LogHandler()
            log.export(f"Failed to factory PostgreSQL database. {e}", path=__file__, err=True)
            exit(1)
