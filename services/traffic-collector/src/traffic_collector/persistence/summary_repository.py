from bson import ObjectId
from pymongo import ASCENDING
from pymongo.database import Database

from traffic_collector.constants.constants import (
    DATE_INDEX,
    TRAFFIC_SUMMARY_DAILY_COLLECTION,
    UNIQUE_INTERFACE_DATE_INDEX,
)
from traffic_collector.domain import DailySummary
from traffic_collector.persistence.connection import translate_database_errors


class SummaryRepository:
    """Access to `traffic_summary_daily`: one document per `(interface_id, date)`."""

    def __init__(self, database: Database) -> None:
        """Receive the database to read from and write to."""
        self._collection = database[TRAFFIC_SUMMARY_DAILY_COLLECTION]

    def ensure_indexes(self) -> None:
        """Create the indexes of the collection if they do not exist (idempotent)."""
        with translate_database_errors():
            self._collection.create_index(
                [("interface_id", ASCENDING), ("date", ASCENDING)],
                name=UNIQUE_INTERFACE_DATE_INDEX,
                unique=True,
            )
            self._collection.create_index([("date", ASCENDING)], name=DATE_INDEX)

    def interface_ids_with_summary(self, date: str) -> set[ObjectId]:
        """Return the interfaces that already have a summary on `date` with a single query."""
        with translate_database_errors():
            documents = self._collection.find({"date": date}, {"_id": 0, "interface_id": 1})
            return {document["interface_id"] for document in documents}

    def save(self, summary: DailySummary) -> None:
        """Store the summary of an interface; idempotent, upsert by `(interface_id, date)`."""
        with translate_database_errors():
            self._collection.update_one(
                {"interface_id": summary.interface_id, "date": summary.date},
                {
                    "$set": {
                        "in_avg": float(summary.in_avg),
                        "out_avg": float(summary.out_avg),
                        "in_max": float(summary.in_max),
                        "out_max": float(summary.out_max),
                    }
                },
                upsert=True,
            )

    def delete_day(self, interface_id: ObjectId, date: str) -> None:
        """Delete the summary of an interface for `date` [RF-021]."""
        with translate_database_errors():
            self._collection.delete_one({"interface_id": interface_id, "date": date})
