from pymongo.database import Database

from traffic_collector.constants.constants import INTERFACES_COLLECTION
from traffic_collector.constants.enums import InterfaceStatus
from traffic_collector.domain import ActiveInterface
from traffic_collector.persistence.connection import translate_database_errors


class InterfaceRepository:
    """Read-only access to the `interfaces` collection. This service never writes it."""

    def __init__(self, database: Database) -> None:
        """Receive the database to read from."""
        self._collection = database[INTERFACES_COLLECTION]

    def layers(self) -> list[str]:
        """Return the distinct layers in ascending order [RF-018, RF-019].

        Layers without active interfaces are included; the caller decides what to do with them.
        """
        with translate_database_errors():
            return sorted(self._collection.distinct("layer"))

    def active_by_layer(self, layer: str) -> list[ActiveInterface]:
        """Return the active interfaces of `layer` with a single query [RF-019]."""
        with translate_database_errors():
            documents = self._collection.find(
                {"layer": layer, "status": InterfaceStatus.ACTIVE},
                {"_id": 1, "scan_url": 1},
            )
            return [
                ActiveInterface(
                    interface_id=document["_id"], scan_url=document["scan_url"]
                )
                for document in documents
            ]
