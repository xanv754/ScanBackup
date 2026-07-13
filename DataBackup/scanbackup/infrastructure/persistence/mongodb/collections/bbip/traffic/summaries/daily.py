from pathlib import Path
from pymongo import ASCENDING
from pymongo.database import Database
from pymongo.errors import CollectionInvalid, BulkWriteError
from scanbackup.shared import (
    FileEmptyError,
    MongoCreateCollectionError,
    MongoExportCollectionError,
    MongoImportCollectionError,
    MongoDeleteCollectionError,
    DataContentError,
)
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
from scanbackup.infrastructure.readers import TrafficDailySummaryBBIPImport
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.summaries import (
    MongoTrafficDailySummaryBBIPDTO,
)
from scanbackup.infrastructure.writers import CSVWriter


class TrafficDailySummaryBBIPCollection(CollectionOperation):
    _NAME = MongoCollectionName.TRAFFIC_DAILY_SUMMARY.value

    @staticmethod
    def create(database: Database) -> None:
        try:
            database.create_collection(
                name=TrafficDailySummaryBBIPCollection._NAME,
                validator=DAILY_SUMMARY_SCHEMA,
            )
            collection = database[TrafficDailySummaryBBIPCollection._NAME]
            collection.create_index(
                [
                    (TrafficDailySummaryBBIPField.DEVICE.value, ASCENDING),
                    (TrafficDailySummaryBBIPField.DATE.value, ASCENDING),
                ],
                unique=True,
                name=f"unique_{TrafficDailySummaryBBIPCollection._NAME.lower()}",
            )
            collection.create_index(
                [(TrafficDailySummaryBBIPField.DATE.value, ASCENDING)],
                name=f"date_{TrafficDailySummaryBBIPCollection._NAME.lower()}",
            )
        except CollectionInvalid as error:
            raise MongoCreateCollectionError(
                TrafficDailySummaryBBIPCollection._NAME,
                error=f"La colección no es válida para creación\n{error}",
            )
        except Exception as error:
            raise MongoCreateCollectionError(
                TrafficDailySummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def delete(database: Database) -> None:
        try:
            collection = database[TrafficDailySummaryBBIPCollection._NAME]
            collection.delete_many({})
            collection.drop()
        except Exception as error:
            raise MongoDeleteCollectionError(
                TrafficDailySummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> str:
        try:
            collection = database[TrafficDailySummaryBBIPCollection._NAME]
            projection = {} if include_id else {"_id": 0}
            documents = collection.find({}, projection)

            data = (
                [MongoTrafficDailySummaryBBIPDTO.from_mongo(doc) for doc in documents]
                if include_id
                else [MongoTrafficDailySummaryBBIPDTO(**doc) for doc in documents]
            )

            writer = CSVWriter(dir=dirpath)
            return writer.export(
                filename=TrafficDailySummaryBBIPCollection._NAME, data=data
            )
        except Exception as error:
            raise MongoExportCollectionError(
                TrafficDailySummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def import_data(
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        try:
            reader = TrafficDailySummaryBBIPImport(delimiter)
            documents = reader.import_data(input_path)

            collection = database[TrafficDailySummaryBBIPCollection._NAME]
            try:
                collection.insert_many(documents, ordered=False)
            except BulkWriteError as bwe:
                non_duplicate_errors = [
                    err
                    for err in bwe.details.get("writeErrors", [])
                    if err.get("code") != 11000
                ]
                if non_duplicate_errors:
                    raise MongoImportCollectionError(
                        TrafficDailySummaryBBIPCollection._NAME, error=bwe
                    )
        except DataContentError:
            raise
        except FileEmptyError:
            return
        except MongoImportCollectionError:
            raise
        except Exception as error:
            raise MongoImportCollectionError(
                TrafficDailySummaryBBIPCollection._NAME, error=error
            )
