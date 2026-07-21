from pathlib import Path
from pymongo import ASCENDING
from pymongo.database import Database
from scanbackup.domain import IPHourSummaryBBIPField
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.ip.summaries.hour import (
    HOUR_SUMMARY_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections.operation import (
    CollectionOperation,
)
from scanbackup.infrastructure.persistence.mongodb.collections import mongo_io
from scanbackup.infrastructure.readers import IPHourSummaryBBIPImport
from scanbackup.infrastructure.writers import CSVWriter
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.ip.summaries import (
    MongoIPHourSummaryBBIPDTO,
)


class IPHourSummaryBBIPCollection(CollectionOperation):
    """Mongo collection for BBIP active-IP hourly summaries (`IP_HOUR_SUMMARY_BBIP`)."""

    _NAME = MongoCollectionName.IP_HOUR_SUMMARY.value
    _INDEXES: tuple[mongo_io.IndexSpec, ...] = (
        (
            [
                (IPHourSummaryBBIPField.DEVICE.value, ASCENDING),
                (IPHourSummaryBBIPField.DATE.value, ASCENDING),
                (IPHourSummaryBBIPField.TIME.value, ASCENDING),
            ],
            True,
            f"unique_{_NAME.lower()}",
        ),
        (
            [(IPHourSummaryBBIPField.DATE.value, ASCENDING)],
            False,
            f"date_{_NAME.lower()}",
        ),
    )

    @staticmethod
    def create(database: Database) -> None:
        mongo_io.create_collection(
            IPHourSummaryBBIPCollection._NAME,
            database,
            HOUR_SUMMARY_SCHEMA,
            IPHourSummaryBBIPCollection._INDEXES,
        )

    @staticmethod
    def delete(database: Database) -> None:
        mongo_io.delete_collection(IPHourSummaryBBIPCollection._NAME, database)

    @staticmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> str:
        return mongo_io.export_collection(
            IPHourSummaryBBIPCollection._NAME,
            database,
            MongoIPHourSummaryBBIPDTO,
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
            IPHourSummaryBBIPCollection._NAME,
            database,
            IPHourSummaryBBIPImport,
            input_path,
            delimiter,
        )
