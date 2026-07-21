from pathlib import Path
from pymongo import ASCENDING
from pymongo.database import Database
from scanbackup.domain import TrafficDailySummaryBBIPField
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.summaries.daily import (
    DAILY_SUMMARY_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections.operation import (
    CollectionOperation,
)
from scanbackup.infrastructure.persistence.mongodb.collections import mongo_io
from scanbackup.infrastructure.readers import TrafficDailySummaryBBIPImport
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.summaries import (
    MongoTrafficDailySummaryBBIPDTO,
)
from scanbackup.infrastructure.writers import CSVWriter


class TrafficDailySummaryBBIPCollection(CollectionOperation):
    """Mongo collection for BBIP traffic daily summaries (`TRAFFIC_DAILY_SUMMARY_BBIP`)."""

    _NAME = MongoCollectionName.TRAFFIC_DAILY_SUMMARY.value
    _INDEXES: tuple[mongo_io.IndexSpec, ...] = (
        (
            [
                (TrafficDailySummaryBBIPField.DEVICE.value, ASCENDING),
                (TrafficDailySummaryBBIPField.DATE.value, ASCENDING),
            ],
            True,
            f"unique_{_NAME.lower()}",
        ),
        (
            [(TrafficDailySummaryBBIPField.DATE.value, ASCENDING)],
            False,
            f"date_{_NAME.lower()}",
        ),
    )

    @staticmethod
    def create(database: Database) -> None:
        mongo_io.create_collection(
            TrafficDailySummaryBBIPCollection._NAME,
            database,
            DAILY_SUMMARY_SCHEMA,
            TrafficDailySummaryBBIPCollection._INDEXES,
        )

    @staticmethod
    def delete(database: Database) -> None:
        mongo_io.delete_collection(TrafficDailySummaryBBIPCollection._NAME, database)

    @staticmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> str:
        return mongo_io.export_collection(
            TrafficDailySummaryBBIPCollection._NAME,
            database,
            MongoTrafficDailySummaryBBIPDTO,
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
            TrafficDailySummaryBBIPCollection._NAME,
            database,
            TrafficDailySummaryBBIPImport,
            input_path,
            delimiter,
        )
