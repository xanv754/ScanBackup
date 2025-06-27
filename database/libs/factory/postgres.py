from database.libs.factory.database import DatabaseFactory
from database.libs.product.postgres import DatabasePostgreSQL
from utils.log import log


class DatabasePostgresFactory(DatabaseFactory):
    """Postgres database factory class."""

    __instance: "DatabasePostgresFactory | None" = None
    __database: DatabasePostgreSQL | None = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(DatabasePostgresFactory, cls).__new__(cls)
        return cls.__instance

    def get_database(self, uri: str) -> DatabasePostgreSQL:
        try:
            if not self.__database:
                self.__database = DatabasePostgreSQL(uri=uri)
            return self.__database
        except Exception as error:
            log.error(f"Failed to factory PostgreSQL database. {error}")
            exit(1)
