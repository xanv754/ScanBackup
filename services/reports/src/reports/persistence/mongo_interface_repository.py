from collections.abc import Sequence

from pymongo.database import Database

from reports.constants.constants import (
    FIELD_CAPACITY_GBPS,
    FIELD_ID,
    FIELD_LAYER,
    FIELD_NAME,
    FIELD_SCAN_URL,
    FIELD_VENDOR,
    INTERFACES_COLLECTION,
)
from reports.domain.models import InterfaceInfo
from reports.persistence.connection import translate_database_errors
from reports.persistence.repositories import InterfaceRepository

INTERFACE_PROJECTION = {
    FIELD_ID: 1,
    FIELD_NAME: 1,
    FIELD_VENDOR: 1,
    FIELD_CAPACITY_GBPS: 1,
    FIELD_LAYER: 1,
    FIELD_SCAN_URL: 1,
}


class MongoInterfaceRepository(InterfaceRepository):
    """`InterfaceRepository` backed by MongoDB. It only reads."""

    def __init__(self, database: Database) -> None:
        """Receive the database that holds the `interfaces` collection."""
        self._collection = database[INTERFACES_COLLECTION]

    def layer_values(self) -> list[str]:
        with translate_database_errors():
            return [
                value
                for value in self._collection.distinct(FIELD_LAYER)
                if isinstance(value, str)
            ]

    def find_by_layer_values(self, stored_values: Sequence[str]) -> list[InterfaceInfo]:
        with translate_database_errors():
            documents = self._collection.find(
                {FIELD_LAYER: {"$in": list(stored_values)}}, INTERFACE_PROJECTION
            )
            return [
                InterfaceInfo(
                    id=document[FIELD_ID],
                    name=str(document.get(FIELD_NAME) or ""),
                    vendor=str(document.get(FIELD_VENDOR) or ""),
                    capacity_gbps=float(document.get(FIELD_CAPACITY_GBPS) or 0),
                    scan_url=str(document.get(FIELD_SCAN_URL) or ""),
                )
                for document in documents
            ]
