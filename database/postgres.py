import psycopg2
from utils.config import ConfigurationHandler
from utils.log import LogHandler

class PostgresDatabase:
    __instance: "PostgresDatabase | None" = None
    __configuration: ConfigurationHandler
    __connection: psycopg2.extensions.connection
    __cursor: psycopg2.extensions.cursor
    connected: bool = False

    def __new__(cls):
        if not cls.__instance:
            cls.__instance =  super(PostgresDatabase, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        try:
            if not hasattr(self, "__initialized"):
                self.__initialized = True
                self.__configuration = ConfigurationHandler()
            self.__open_connection()
        except Exception as e:
            LogHandler.log(f"Failed to connect to database. {e}", path=__file__, err=True)

    @classmethod
    def set_uri(cls, uri: str) -> "PostgresDatabase":
        instance = cls.__new__(cls)
        instance.__init__()
        instance.__configuration.set_uri(uri)
        instance.__open_connection()
        return instance

    def __open_connection(self) -> None:
        """Open connection to database."""
        try:
            if hasattr(self, "__connection") and self.__connection:
                self.close_connection()
            uri = self.__configuration.uri_postgres
            self.__connection = psycopg2.connect(uri)
            self.__cursor = self.__connection.cursor()
        except Exception as e:
            LogHandler.log(f"Failed to connect to database. {e}", path=__file__, err=True)
        else:
            self.connected = True

    def get_connection(self) -> psycopg2.extensions.connection:
        """Get connection to database."""
        return self.__connection

    def get_cursor(self) -> psycopg2.extensions.cursor:
        """Get cursor to database."""
        return self.__cursor

    def close_connection(self) -> None:
        """Close connection to database."""
        if hasattr(self, "__cursor") and self.__cursor:
            self.__cursor.close()
        if not hasattr(self, "__connection") and self.__connection:
            self.__connection.close()
