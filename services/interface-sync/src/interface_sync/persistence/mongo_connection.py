from pymongo import MongoClient
from pymongo.database import Database

from interface_sync.constants.constants import MONGO_SERVER_SELECTION_TIMEOUT_MS
from interface_sync.persistence.mongo_settings import MongoSettings


class MongoConnection:
    """Owns the synchronous MongoDB client of the run; `close` must be called when it ends.

    The client is timezone-aware so stored dates are always read back as UTC `datetime`.
    """

    def __init__(self, settings: MongoSettings) -> None:
        """Create the client; no network access happens until the first operation."""
        self._client: MongoClient = MongoClient(
            host=settings.host,
            port=settings.port,
            username=settings.username,
            password=settings.password,
            authSource=settings.auth_source,
            tz_aware=True,
            serverSelectionTimeoutMS=MONGO_SERVER_SELECTION_TIMEOUT_MS,
        )
        self._database = self._client[settings.database]

    @property
    def database(self) -> Database:
        """Return the database of the service."""
        return self._database

    def close(self) -> None:
        """Release the client resources."""
        self._client.close()
