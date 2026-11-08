from collections.abc import Iterator
from contextlib import contextmanager

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

from traffic_collector.constants.constants import MONGO_SERVER_SELECTION_TIMEOUT_MS
from traffic_collector.exceptions import DatabaseError
from traffic_collector.settings import MongoSettings


@contextmanager
def translate_database_errors() -> Iterator[None]:
    """Turn any PyMongo failure inside the block into `DatabaseError`."""
    try:
        yield
    except PyMongoError as error:
        raise DatabaseError(type(error).__name__) from error


class MongoConnection:
    """Owns the MongoDB client of the run. Created once in the composition root."""

    def __init__(self, settings: MongoSettings) -> None:
        """Create the client; no connection is made until the first operation."""
        self._client: MongoClient = MongoClient(
            host=settings.host,
            port=settings.port,
            username=settings.username,
            password=settings.password,
            authSource=settings.auth_source,
            serverSelectionTimeoutMS=MONGO_SERVER_SELECTION_TIMEOUT_MS,
            tz_aware=True,
        )
        self._database_name = settings.database

    @property
    def database(self) -> Database:
        """Return the database used by the service."""
        return self._client[self._database_name]

    def verify(self) -> None:
        """Raise `DatabaseError` if the database is not available."""
        with translate_database_errors():
            self._client.admin.command("ping")

    def close(self) -> None:
        """Close the client."""
        self._client.close()
