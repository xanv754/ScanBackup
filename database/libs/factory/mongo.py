from database.libs.factory.database import DatabaseFactory
from database.libs.product.mongo import DatabaseMongo
from utils.log import log


class DatabaseMongoFactory(DatabaseFactory):
    """Mongo database factory class."""

    __instance: "DatabaseMongoFactory | None" = None
    __database: DatabaseMongo | None = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(DatabaseMongoFactory, cls).__new__(cls)
        return cls.__instance

    def get_database(self, uri: str) -> DatabaseMongo:
        try:
            if not self.__database:
                self.__database = DatabaseMongo(uri=uri)
            return self.__database
        except Exception as error:
            log.error(f"Failed to factory MongoDB database. {error}")
            exit(1)