import psycopg2
from psycopg2 import sql
from database.constant.tables import TableNameDatabase
from database.schemas.postgres.borde import BORDE_SCHEMA, BORDE_SECUENCE_SCHEMA
from database.schemas.postgres.bras import BRAS_SCHEMA, BRAS_SECUENCE_SCHEMA
from database.schemas.postgres.caching import CACHING_SCHEMA, CACHING_SECUENCE_SCHEMA
from database.schemas.postgres.rai import RAI_SCHEMA, RAI_SECUENCE_SCHEMA
from database.schemas.postgres.trafficHistory import TRAFFIC_HISTORY_SCHEMA
from database.schemas.postgres.ipHistory import IP_HISTORY_SCHEMA
from database.database.product.database import Database
from utils.log import LogHandler

class PostgresDatabase(Database):
    __connection: psycopg2.extensions.connection
    __cursor: psycopg2.extensions.cursor
    connected: bool = False

    def __init__(self, uri: str):
        try:
            if not self.__check_database(uri):
                self.__create_database(uri)
            self.__connection = psycopg2.connect(uri)
            self.__cursor = self.__connection.cursor()
        except Exception as e:
            LogHandler.log(f"Failed to connect to PostgreSQL database. {e}", path=__file__, err=True)
        else:
            self.connected = True

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
            LogHandler.log(f"PostgreSQL database error. {e}", err=True)
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
            LogHandler.log(f"PostgreSQL database Error. {e}", err=True)
            return False
        else:
            return True

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
            cursor = self.__cursor
            cursor.execute(BORDE_SECUENCE_SCHEMA)
            cursor.execute(BORDE_SCHEMA)
            cursor.execute(BRAS_SECUENCE_SCHEMA)
            cursor.execute(BRAS_SCHEMA)
            cursor.execute(CACHING_SECUENCE_SCHEMA)
            cursor.execute(CACHING_SCHEMA)
            cursor.execute(RAI_SECUENCE_SCHEMA)
            cursor.execute(RAI_SCHEMA)
            cursor.execute(TRAFFIC_HISTORY_SCHEMA)
            cursor.execute(IP_HISTORY_SCHEMA)
            self.__connection.commit()
            self.close_connection()
        except Exception as e:
            LogHandler.log(f"PostgreSQL database Error. {e}", err=True)
            return False
        else:
            return True

    def rollback(self) -> bool:
        try:
            cursor = self.__cursor
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.BORDE}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.BRAS}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.CACHING}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.RAI}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.TRAFFIC_HISTORY}")
            cursor.execute(f"DROP TABLE IF EXISTS {TableNameDatabase.IP_HISTORY}")
            self.__connection.commit()
            self.close_connection()
        except Exception as e:
            LogHandler.log(f"PostgreSQL database Error. {e}", err=True)
            return False
        else:
            return True
