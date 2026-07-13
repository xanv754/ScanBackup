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
from scanbackup.infrastructure.readers import IPHourSummaryBBIPImport
from scanbackup.infrastructure.writers import CSVWriter
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.ip.summaries import (
    MongoIPHourSummaryBBIPDTO,
)


class IPHourSummaryBBIPCollection(CollectionOperation):
    _NAME = MongoCollectionName.IP_HOUR_SUMMARY.value

    @staticmethod
    def create(database: Database) -> None:
        try:
            database.create_collection(
                name=IPHourSummaryBBIPCollection._NAME,
                validator=HOUR_SUMMARY_SCHEMA,
            )
            collection = database[IPHourSummaryBBIPCollection._NAME]
            collection.create_index(
                [
                    (IPHourSummaryBBIPField.DEVICE.value, ASCENDING),
                    (IPHourSummaryBBIPField.DATE.value, ASCENDING),
                    (IPHourSummaryBBIPField.TIME.value, ASCENDING),
                ],
                unique=True,
                name=f"unique_{IPHourSummaryBBIPCollection._NAME.lower()}",
            )
            collection.create_index(
                [(IPHourSummaryBBIPField.DATE.value, ASCENDING)],
                name=f"date_{IPHourSummaryBBIPCollection._NAME.lower()}",
            )
        except CollectionInvalid as error:
            raise MongoCreateCollectionError(
                IPHourSummaryBBIPCollection._NAME,
                error=f"La colección no es válida para creación\n{error}",
            )
        except Exception as error:
            raise MongoCreateCollectionError(
                IPHourSummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def delete(database: Database) -> None:
        try:
            collection = database[IPHourSummaryBBIPCollection._NAME]
            collection.delete_many({})
            collection.drop()
        except Exception as error:
            raise MongoDeleteCollectionError(
                IPHourSummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> str:
        try:
            collection = database[IPHourSummaryBBIPCollection._NAME]
            projection = {} if include_id else {"_id": 0}
            documents = collection.find({}, projection)

            data = (
                [MongoIPHourSummaryBBIPDTO.from_mongo(doc) for doc in documents]
                if include_id
                else [MongoIPHourSummaryBBIPDTO(**doc) for doc in documents]
            )

            writer = CSVWriter(dir=dirpath)
            return writer.export(
                filename=IPHourSummaryBBIPCollection._NAME, data=data
            )
        except Exception as error:
            raise MongoExportCollectionError(
                IPHourSummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def import_data(
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        try:
            reader = IPHourSummaryBBIPImport(delimiter)
            documents = reader.import_data(input_path)

            collection = database[IPHourSummaryBBIPCollection._NAME]
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
                        IPHourSummaryBBIPCollection._NAME, error=bwe
                    )
        except FileEmptyError:
            return
        except DataContentError:
            raise
        except MongoImportCollectionError:
            raise
        except Exception as error:
            raise MongoImportCollectionError(
                IPHourSummaryBBIPCollection._NAME, error=error
            )
