from bson import ObjectId
from pymongo.database import Database

from traffic_collector.constants.constants import TRAFFIC_SUMMARY_DAILY_COLLECTION
from traffic_collector.persistence.connection import translate_database_errors


class SummaryRepository:
    """Deletes daily summaries when a day is forced. Writing summaries belongs to RF-026."""

    def __init__(self, database: Database) -> None:
        """Receive the database to delete from."""
        self._collection = database[TRAFFIC_SUMMARY_DAILY_COLLECTION]

    def delete_day(self, interface_id: ObjectId, date: str) -> None:
        """Delete the summary of an interface for `date` [RF-021]."""
        with translate_database_errors():
            self._collection.delete_one({"interface_id": interface_id, "date": date})
