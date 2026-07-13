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
from scanbackup.infrastructure.readers import TrafficHourSummaryBBIPImport
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.summaries import (
    MongoTrafficHourSummaryBBIPDTO,
)
from scanbackup.infrastructure.writers import CSVWriter


class TrafficHourSummaryBBIPCollection(CollectionOperation):
    _NAME = MongoCollectionName.TRAFFIC_HOUR_SUMMARY.value

    @staticmethod
    def create(database: Database) -> None:
        try:
            database.create_collection(
                name=TrafficHourSummaryBBIPCollection._NAME,
                validator=HOUR_SUMMARY_SCHEMA,
            )
            collection = database[TrafficHourSummaryBBIPCollection._NAME]
            collection.create_index(
                [
                    (TrafficHourSummaryBBIPField.DEVICE.value, ASCENDING),
                    (TrafficHourSummaryBBIPField.DATE.value, ASCENDING),
                    (TrafficHourSummaryBBIPField.TIME.value, ASCENDING),
                ],
                unique=True,
                name=f"unique_{TrafficHourSummaryBBIPCollection._NAME.lower()}",
            )
            collection.create_index(
                [(TrafficHourSummaryBBIPField.DATE.value, ASCENDING)],
                name=f"date_{TrafficHourSummaryBBIPCollection._NAME.lower()}",
            )
        except CollectionInvalid as error:
            raise MongoCreateCollectionError(
                TrafficHourSummaryBBIPCollection._NAME,
                error=f"La colección no es válida para creación\n{error}",
            )
        except Exception as error:
            raise MongoCreateCollectionError(
                TrafficHourSummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def delete(database: Database) -> None:
        try:
            collection = database[TrafficHourSummaryBBIPCollection._NAME]
            collection.delete_many({})
            collection.drop()
        except Exception as error:
            raise MongoDeleteCollectionError(
                TrafficHourSummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> str:
        try:
            collection = database[TrafficHourSummaryBBIPCollection._NAME]
            projection = {} if include_id else {"_id": 0}
            documents = collection.find({}, projection)

            data = (
                [MongoTrafficHourSummaryBBIPDTO.from_mongo(doc) for doc in documents]
                if include_id
                else [MongoTrafficHourSummaryBBIPDTO(**doc) for doc in documents]
            )

            writer = CSVWriter(dir=dirpath)
            return writer.export(
                filename=TrafficHourSummaryBBIPCollection._NAME, data=data
            )
        except Exception as error:
            raise MongoExportCollectionError(
                TrafficHourSummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def import_data(
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        try:
            reader = TrafficHourSummaryBBIPImport(delimiter)
            documents = reader.import_data(input_path)

            collection = database[TrafficHourSummaryBBIPCollection._NAME]
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
                        TrafficHourSummaryBBIPCollection._NAME, error=bwe
                    )
        except DataContentError:
            raise
        except FileEmptyError:
            return
        except MongoImportCollectionError:
            raise
        except Exception as error:
            raise MongoImportCollectionError(
                TrafficHourSummaryBBIPCollection._NAME, error=error
            )
