from database.libs.factory.database import DatabaseFactory
from database.libs.product.mongo import MongoDatabase
from utils.log import log

class MongoDatabaseFactory(DatabaseFactory):
    """Mongo database factory class."""

    __instance: "MongoDatabaseFactory | None" = None
    __database: MongoDatabase | None = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(MongoDatabaseFactory, cls).__new__(cls)
        return cls.__instance

    def get_database(self, uri: str) -> MongoDatabase:
        try:
            if not self.__database:
                self.__database = MongoDatabase(uri=uri)
            return self.__database
        except Exception as error:
            log.error(f"Failed to factory MongoDB database. {error}")
            exit(1)