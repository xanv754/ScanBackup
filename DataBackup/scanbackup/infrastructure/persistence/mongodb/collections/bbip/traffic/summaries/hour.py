from pathlib import Path
from pymongo import ASCENDING
from pymongo.database import Database
from scanbackup.domain import TrafficHourSummaryBBIPField
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.summaries.hour import (
    HOUR_SUMMARY_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections.operation import (
    CollectionOperation,
)
from scanbackup.infrastructure.persistence.mongodb.collections import mongo_io
from scanbackup.infrastructure.readers import TrafficHourSummaryBBIPImport
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.summaries import (
    MongoTrafficHourSummaryBBIPDTO,
)
from scanbackup.infrastructure.writers import CSVWriter


class TrafficHourSummaryBBIPCollection(CollectionOperation):
    """Mongo collection for BBIP traffic hourly summaries (`TRAFFIC_HOUR_SUMMARY_BBIP`)."""

    _NAME = MongoCollectionName.TRAFFIC_HOUR_SUMMARY.value
    _INDEXES: tuple[mongo_io.IndexSpec, ...] = (
        (
            [
                (TrafficHourSummaryBBIPField.DEVICE.value, ASCENDING),
                (TrafficHourSummaryBBIPField.DATE.value, ASCENDING),
                (TrafficHourSummaryBBIPField.TIME.value, ASCENDING),
            ],
            True,
            f"unique_{_NAME.lower()}",
        ),
        (
            [(TrafficHourSummaryBBIPField.DATE.value, ASCENDING)],
            False,
            f"date_{_NAME.lower()}",
        ),
    )

    @staticmethod
    def create(database: Database) -> None:
        mongo_io.create_collection(
            TrafficHourSummaryBBIPCollection._NAME,
            database,
            HOUR_SUMMARY_SCHEMA,
            TrafficHourSummaryBBIPCollection._INDEXES,
        )

    @staticmethod
    def delete(database: Database) -> None:
        mongo_io.delete_collection(TrafficHourSummaryBBIPCollection._NAME, database)

    @staticmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> str:
        return mongo_io.export_collection(
            TrafficHourSummaryBBIPCollection._NAME,
            database,
            MongoTrafficHourSummaryBBIPDTO,
            CSVWriter,
            dirpath,
            include_id,
        )

    @staticmethod
    def import_data(
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        mongo_io.import_insert_many(
            TrafficHourSummaryBBIPCollection._NAME,
            database,
            TrafficHourSummaryBBIPImport,
            input_path,
            delimiter,
        )
