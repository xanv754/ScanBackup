from pathlib import Path
from pymongo import ASCENDING
from pymongo.database import Database
from pymongo.errors import CollectionInvalid, BulkWriteError
from scanbackup.shared import (
    DataContentError,
    FileEmptyError,
    MongoCreateCollectionError,
    MongoExportCollectionError,
    MongoImportCollectionError,
    MongoDeleteCollectionError,
)
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
from scanbackup.infrastructure.readers import IPDailySummaryBBIPImport
from scanbackup.infrastructure.writers import CSVWriter
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.ip.summaries import (
    MongoIPDailySummaryBBIPDTO,
)


class IPDailySummaryBBIPCollection(CollectionOperation):
    _NAME = MongoCollectionName.IP_DAILY_SUMMARY.value

    @staticmethod
    def create(database: Database) -> None:
        try:
            database.create_collection(
                name=IPDailySummaryBBIPCollection._NAME,
                validator=DAILY_SUMMARY_SCHEMA,
            )
            collection = database[IPDailySummaryBBIPCollection._NAME]
            collection.create_index(
                [
                    (IPDailySummaryBBIPField.DEVICE.value, ASCENDING),
                    (IPDailySummaryBBIPField.DATE.value, ASCENDING),
                ],
                unique=True,
                name=f"unique_{IPDailySummaryBBIPCollection._NAME.lower()}",
            )
            collection.create_index(
                [(IPDailySummaryBBIPField.DATE.value, ASCENDING)],
                name=f"date_{IPDailySummaryBBIPCollection._NAME.lower()}",
            )
        except CollectionInvalid as error:
            raise MongoCreateCollectionError(
                IPDailySummaryBBIPCollection._NAME,
                error=f"La colección no es válida para creación\n{error}",
            )
        except Exception as error:
            raise MongoCreateCollectionError(
                IPDailySummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def delete(database: Database) -> None:
        try:
            collection = database[IPDailySummaryBBIPCollection._NAME]
            collection.delete_many({})
            collection.drop()
        except Exception as error:
            raise MongoDeleteCollectionError(
                IPDailySummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def export_data(
        database: Database,
        include_id: bool = False,
    ) -> str:
        try:
            collection = database[IPDailySummaryBBIPCollection._NAME]
            projection = {} if include_id else {"_id": 0}
            documents = collection.find({}, projection)

            data = (
                [MongoIPDailySummaryBBIPDTO.from_mongo(doc) for doc in documents]
                if include_id
                else [MongoIPDailySummaryBBIPDTO(**doc) for doc in documents]
            )

            writer = CSVWriter()
            return writer.export(
                filename=IPDailySummaryBBIPCollection._NAME, data=data
            )
        except Exception as error:
            raise MongoExportCollectionError(
                IPDailySummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def import_data(
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        try:
            reader = IPDailySummaryBBIPImport(delimiter)
            documents = reader.import_data(input_path)

            collection = database[IPDailySummaryBBIPCollection._NAME]
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
                        IPDailySummaryBBIPCollection._NAME, error=bwe
                    )
        except FileEmptyError:
            return
        except DataContentError:
            raise
        except MongoImportCollectionError:
            raise
        except Exception as error:
            raise MongoImportCollectionError(
                IPDailySummaryBBIPCollection._NAME, error=error
            )
