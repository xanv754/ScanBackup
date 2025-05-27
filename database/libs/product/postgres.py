import psycopg2
from psycopg2 import sql
from database import (
    TableNameDatabase,
    Database,
    BORDE_SECUENCE_SCHEMA_POSTGRES,
    BORDE_SCHEMA_POSTGRES,
    BRAS_SECUENCE_SCHEMA_POSTGRES,
    BRAS_SCHEMA_POSTGRES,
    CACHING_SECUENCE_SCHEMA_POSTGRES,
    CACHING_SCHEMA_POSTGRES,
    RAI_SECUENCE_SCHEMA_POSTGRES,
    RAI_SCHEMA_POSTGRES,
    TRAFFIC_HISTORY_SCHEMA_POSTGRES,
    IP_HISTORY_SCHEMA_POSTGRES,
    DAILY_REPORT_SCHEMA_POSTGRES
)
from utils.log import log

class PostgresDatabase(Database):
    __connection: psycopg2.extensions.connection
    __cursor: psycopg2.extensions.cursor
    __uri: str
    connected: bool = False

    def __init__(self, uri: str):
        self.__uri = uri

    def __check_database(self, uri: str) -> bool:
        """Check if the database exists."""
        try:
            name_db = uri.split("/")[-1]
            uri_base = f"postgres://{uri.split("/")[-2]}/postgres"
            connection = psycopg2.connect(uri_base)
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(
                """
                    SELECT
                        1
                    FROM
                        pg_database
                    WHERE
                        datname = %s
                """,
                (name_db,),
            )
            status = cursor.fetchone() is not None
            cursor.close()
            connection.close()
        except Exception as e:
            log.error(f"PostgreSQL database error. {e}")
            return False
        else:
            return status

    def __create_database(self, uri: str) -> bool:
        """Create the database (if not exists)."""
        try:
            name_db = uri.split("/")[-1].strip()
            uri_base = f"postgres://{uri.split("/")[-2]}/postgres"
            connection = psycopg2.connect(uri_base)
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(
                sql.SQL(
                    """
                        CREATE DATABASE {db}
                    """
                ).format(
                    db=sql.Identifier(name_db)
                )
            )
            cursor.close()
            connection.close()
        except Exception as e:
            log.error(f"PostgreSQL database Error. {e}")
            return False
        else:
            return True
        
    def open_connection(self) -> None:
        try:
            if not self.__check_database(self.__uri):
                self.__create_database(self.__uri)
            self.__connection = psycopg2.connect(self.__uri)
            self.__cursor = self.__connection.cursor()
        except Exception as e:
            log.error(f"Failed to connect to PostgreSQL database. {e}")
            self.connected = False
        else:
            self.connected = True

    def get_connection(self) -> psycopg2.extensions.connection:
        return self.__connection

    def get_cursor(self, table: str | None = None) -> psycopg2.extensions.cursor:
        return self.__cursor

    def close_connection(self) -> None:
        self.__cursor.close()
        self.__connection.close()
        self.connected = False

    def migration(self) -> bool:
        try:
            self.open_connection()
            cursor = self.__cursor
            cursor.execute(BORDE_SECUENCE_SCHEMA_POSTGRES)
            cursor.execute(BORDE_SCHEMA_POSTGRES)
            cursor.execute(BRAS_SECUENCE_SCHEMA_POSTGRES)
            cursor.execute(BRAS_SCHEMA_POSTGRES)
            cursor.execute(CACHING_SECUENCE_SCHEMA_POSTGRES)
            cursor.execute(CACHING_SCHEMA_POSTGRES)
            cursor.execute(RAI_SECUENCE_SCHEMA_POSTGRES)
            cursor.execute(RAI_SCHEMA_POSTGRES)
            cursor.execute(TRAFFIC_HISTORY_SCHEMA_POSTGRES)
            cursor.execute(IP_HISTORY_SCHEMA_POSTGRES)
            cursor.execute(DAILY_REPORT_SCHEMA_POSTGRES)
            self.__connection.commit()
            self.close_connection()
        except Exception as e:
            log.error(f"PostgreSQL database Error. {e}")
            return False
        else:
            return True

    def rollback(self) -> bool:
        try:
            self.open_connection()
            cursor = self.__cursor
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.BORDE}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.BRAS}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.CACHING}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.RAI}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.TRAFFIC_HISTORY}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.IP_HISTORY}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.DAILY_REPORT}")
            self.__connection.commit()
            self.close_connection()
        except Exception as e:
            log.error(f"PostgreSQL database Error. {e}")
            return False
        else:
            return True
