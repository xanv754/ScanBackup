import psycopg2
from psycopg2 import sql
from database.product.database import Database
from utils.log import LogHandler

class PostgresDatabase(Database):
    __connection: psycopg2.extensions.connection
    __cursor: psycopg2.extensions.cursor
    connected: bool = False

    def __init__(self, uri: str):
        try:
            self.__connection = psycopg2.connect(uri)
            self.__cursor = self.__connection.cursor()
        except Exception as e:
            LogHandler.log(f"Failed to connect to PostgreSQL database. {e}", path=__file__, err=True)
        else:
            self.connected = True

    def __check_database(self) -> bool:
        """Check if the database exists.

        Returns
        -------
        If True, the database exists. Otherwise returns False.
        """
        try:
            uri = self.__configuration.uri_postgres
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
                        datname = %
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
        
    def __create_database(self) -> bool:
        """Create the database (if not exists).

        Returns
        --------
        Operation status. If True, the database exists or has been created correctly. Otherwise returns False.
        """
        try:
            uri = self.__configuration.uri_postgres
            name_db = uri.split("/")[-1]
            uri_base = f"postgres://{uri.split("/")[-2]}/postgres"
            connection = psycopg2.connect(uri)
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(
                sql.SQL(
                    """
                        CREATE DATABASE
                            {db}
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

    def migration(self) -> bool:
        return True

    def rollback(self) -> bool:
        return True

    
