from pathlib import Path
from pymongo import ASCENDING
from pymongo.database import Database
from scanbackup.domain import IPDailySummaryBBIPField
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.ip.summaries.daily import (
    DAILY_SUMMARY_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections.operation import (
    CollectionOperation,
)
from scanbackup.infrastructure.persistence.mongodb.collections import mongo_io
from scanbackup.infrastructure.readers import IPDailySummaryBBIPImport
from scanbackup.infrastructure.writers import CSVWriter
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.ip.summaries import (
    MongoIPDailySummaryBBIPDTO,
)


class IPDailySummaryBBIPCollection(CollectionOperation):
    """Mongo collection for BBIP active-IP daily summaries (`IP_DAILY_SUMMARY_BBIP`)."""

    _NAME = MongoCollectionName.IP_DAILY_SUMMARY.value
    _INDEXES: tuple[mongo_io.IndexSpec, ...] = (
        (
            [
                (IPDailySummaryBBIPField.DEVICE.value, ASCENDING),
                (IPDailySummaryBBIPField.DATE.value, ASCENDING),
            ],
            True,
            f"unique_{_NAME.lower()}",
        ),
        (
            [(IPDailySummaryBBIPField.DATE.value, ASCENDING)],
            False,
            f"date_{_NAME.lower()}",
        ),
    )

    @staticmethod
    def create(database: Database) -> None:
        mongo_io.create_collection(
            IPDailySummaryBBIPCollection._NAME,
            database,
            DAILY_SUMMARY_SCHEMA,
            IPDailySummaryBBIPCollection._INDEXES,
        )

    @staticmethod
    def delete(database: Database) -> None:
        mongo_io.delete_collection(IPDailySummaryBBIPCollection._NAME, database)

    @staticmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> str:
        return mongo_io.export_collection(
            IPDailySummaryBBIPCollection._NAME,
            database,
            MongoIPDailySummaryBBIPDTO,
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
            IPDailySummaryBBIPCollection._NAME,
            database,
            IPDailySummaryBBIPImport,
            input_path,
            delimiter,
        )
