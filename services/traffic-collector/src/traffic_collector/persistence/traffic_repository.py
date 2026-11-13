from collections.abc import Callable, Iterator
from datetime import UTC, datetime

from bson import ObjectId
from pymongo import ASCENDING
from pymongo.database import Database

from traffic_collector.constants.constants import (
    DATE_INDEX,
    TRAFFIC_DAILY_COLLECTION,
    UNIQUE_INTERFACE_DATE_INDEX,
)
from traffic_collector.domain import DailyTraffic, Sample
from traffic_collector.persistence.connection import translate_database_errors


def current_utc_time() -> datetime:
    """Return the current moment in UTC."""
    return datetime.now(UTC)


class TrafficRepository:
    """Access to the raw traffic of `traffic_daily`: one document per `(interface_id, date)`."""

    def __init__(
        self, database: Database, clock: Callable[[], datetime] = current_utc_time
    ) -> None:
        """Receive the database and the clock that stamps `created_at` and `updated_at`."""
        self._collection = database[TRAFFIC_DAILY_COLLECTION]
        self._clock = clock

    def ensure_indexes(self) -> None:
        """Create the indexes of the collection if they do not exist (idempotent)."""
        with translate_database_errors():
            self._collection.create_index(
                [("interface_id", ASCENDING), ("date", ASCENDING)],
                name=UNIQUE_INTERFACE_DATE_INDEX,
                unique=True,
            )
            self._collection.create_index([("date", ASCENDING)], name=DATE_INDEX)

    def interface_ids_with_samples(self, layer: str, date: str) -> set[ObjectId]:
        """Return the interfaces of `layer` that already have samples on `date`.

        A single query per layer [RF-020]. A document with empty `samples` does not count, so
        its interface is collected again.
        """
        with translate_database_errors():
            documents = self._collection.find(
                {"date": date, "layer": layer, "samples.0": {"$exists": True}},
                {"_id": 0, "interface_id": 1},
            )
            return {document["interface_id"] for document in documents}

    def daily_by_date(self, date: str) -> Iterator[DailyTraffic]:
        """Stream the stored days of every interface on `date` with a single cursor."""
        with translate_database_errors():
            documents = self._collection.find(
                {"date": date}, {"interface_id": 1, "layer": 1, "date": 1, "samples": 1}
            )
            for document in documents:
                yield DailyTraffic(
                    interface_id=document["interface_id"],
                    layer=document["layer"],
                    date=document["date"],
                    samples=tuple(
                        Sample(
                            ts=sample["ts"],
                            in_avg=float(sample["in_avg"]),
                            out_avg=float(sample["out_avg"]),
                            in_max=float(sample["in_max"]),
                            out_max=float(sample["out_max"]),
                        )
                        for sample in document["samples"]
                    ),
                )

    def save(self, daily_traffic: DailyTraffic) -> None:
        """Store the day of an interface; idempotent and safe to repeat [RF-025].

        Upsert by `(interface_id, date)`: `layer`, `samples` and `updated_at` are always
        replaced and `created_at` is set only on insert. An existing document with empty
        `samples` is completed.
        """
        moment = self._clock()
        with translate_database_errors():
            self._collection.update_one(
                {"interface_id": daily_traffic.interface_id, "date": daily_traffic.date},
                {
                    "$set": {
                        "layer": daily_traffic.layer,
                        "samples": [self._to_document(sample) for sample in daily_traffic.samples],
                        "updated_at": moment,
                    },
                    "$setOnInsert": {"created_at": moment},
                },
                upsert=True,
            )

    def delete_day(self, interface_id: ObjectId, date: str) -> None:
        """Delete the raw document of an interface for `date` [RF-021]."""
        with translate_database_errors():
            self._collection.delete_one({"interface_id": interface_id, "date": date})

    @staticmethod
    def _to_document(sample: Sample) -> dict:
        """Return the stored form of a sample, with every value as `float`."""
        return {
            "ts": sample.ts,
            "in_avg": float(sample.in_avg),
            "out_avg": float(sample.out_avg),
            "in_max": float(sample.in_max),
            "out_max": float(sample.out_max),
        }
