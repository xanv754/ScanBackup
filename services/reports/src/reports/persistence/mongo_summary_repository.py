from collections.abc import Iterator, Sequence

from bson import ObjectId
from pymongo.database import Database

from reports.constants.constants import (
    FIELD_DATE,
    FIELD_DAYS,
    FIELD_ID,
    FIELD_IN_AVG,
    FIELD_IN_MAX,
    FIELD_INTERFACE_ID,
    FIELD_OUT_AVG,
    FIELD_OUT_MAX,
    LOOKUP_BATCH_SIZE,
    TRAFFIC_SUMMARY_DAILY_COLLECTION,
)
from reports.domain.date_range import DateRange
from reports.domain.models import AggregatedSummary
from reports.persistence.connection import translate_database_errors
from reports.persistence.repositories import DailySummaryRepository


class MongoDailySummaryRepository(DailySummaryRepository):
    """`DailySummaryRepository` backed by MongoDB. It only aggregates, it never writes.

    The ids are sent in batches so the `$in` list stays small. Each interface belongs to one
    batch, so the results of the batches are simply concatenated. Before the `$group` a `$sort`
    by interface and date, backed by the unique index, fixes the order in which `$avg`
    accumulates, so the same data always gives the same result [RF-031].
    """

    def __init__(self, database: Database) -> None:
        """Receive the database that holds the `traffic_summary_daily` collection."""
        self._collection = database[TRAFFIC_SUMMARY_DAILY_COLLECTION]

    def aggregate(
        self, interface_ids: Sequence[ObjectId], date_range: DateRange
    ) -> list[AggregatedSummary]:
        summaries: list[AggregatedSummary] = []
        with translate_database_errors():
            for batch in self._batches(interface_ids):
                pipeline = [
                    self._match_stage(batch, date_range),
                    {"$sort": {FIELD_INTERFACE_ID: 1, FIELD_DATE: 1}},
                    {
                        "$group": {
                            FIELD_ID: f"${FIELD_INTERFACE_ID}",
                            FIELD_IN_AVG: {"$avg": f"${FIELD_IN_AVG}"},
                            FIELD_OUT_AVG: {"$avg": f"${FIELD_OUT_AVG}"},
                            FIELD_IN_MAX: {"$max": f"${FIELD_IN_MAX}"},
                            FIELD_OUT_MAX: {"$max": f"${FIELD_OUT_MAX}"},
                            FIELD_DAYS: {"$sum": 1},
                        }
                    },
                ]
                summaries.extend(
                    AggregatedSummary(
                        interface_id=document[FIELD_ID],
                        in_average_bps=float(document[FIELD_IN_AVG]),
                        out_average_bps=float(document[FIELD_OUT_AVG]),
                        in_max_bps=float(document[FIELD_IN_MAX]),
                        out_max_bps=float(document[FIELD_OUT_MAX]),
                        days=int(document[FIELD_DAYS]),
                    )
                    for document in self._collection.aggregate(pipeline, allowDiskUse=True)
                )
        return summaries

    def dates_with_summary(
        self, interface_ids: Sequence[ObjectId], date_range: DateRange
    ) -> set[str]:
        dates: set[str] = set()
        with translate_database_errors():
            for batch in self._batches(interface_ids):
                pipeline = [
                    self._match_stage(batch, date_range),
                    {"$group": {FIELD_ID: f"${FIELD_DATE}"}},
                ]
                dates.update(
                    document[FIELD_ID] for document in self._collection.aggregate(pipeline)
                )
        return dates

    @staticmethod
    def _match_stage(interface_ids: Sequence[ObjectId], date_range: DateRange) -> dict:
        """Return the `$match` of the interfaces and the range, compared as `YYYY-MM-DD` text."""
        return {
            "$match": {
                FIELD_INTERFACE_ID: {"$in": list(interface_ids)},
                FIELD_DATE: {"$gte": date_range.start_key, "$lte": date_range.end_key},
            }
        }

    @staticmethod
    def _batches(interface_ids: Sequence[ObjectId]) -> Iterator[Sequence[ObjectId]]:
        """Yield the ids in slices of at most `LOOKUP_BATCH_SIZE`."""
        for offset in range(0, len(interface_ids), LOOKUP_BATCH_SIZE):
            yield interface_ids[offset : offset + LOOKUP_BATCH_SIZE]
