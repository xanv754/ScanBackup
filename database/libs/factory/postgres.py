from database import DatabaseFactory, PostgresDatabase
from utils import log


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
            if not self.__database:
                self.__database = PostgresDatabase(uri=uri)
            return self.__database
        except Exception as error:
            log.error(f"Failed to factory PostgreSQL database. {error}")
            exit(1)
