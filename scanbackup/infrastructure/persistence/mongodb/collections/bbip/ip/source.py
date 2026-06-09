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
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.ip.source import (
    IPSourceBBIPField,
    SOURCE_IP_BBIP_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections.operation import (
    CollectionOperation,
)
from scanbackup.infrastructure.readers import IPSourceBBIPImport
from scanbackup.infrastructure.writers import CSVWriter
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.ip.source import (
    MongoIPSourceBBIPDTO,
)


class IPSourceBBIPCollection(CollectionOperation):
    _NAME = MongoCollectionName.IP_SOURCES.value

    @staticmethod
    def create(database: Database) -> None:
        name_collection = IPSourceBBIPCollection._NAME
        try:
            database.create_collection(
                name=name_collection, validator=SOURCE_IP_BBIP_SCHEMA
            )
            collection = database[name_collection]
            collection.create_index(
                [
                    (IPSourceBBIPField.LAYER.value, ASCENDING),
                    (IPSourceBBIPField.TYPE.value, ASCENDING),
                    (IPSourceBBIPField.CAPACITY.value, ASCENDING),
                    (IPSourceBBIPField.INTERFACE.value, ASCENDING),
                ],
                unique=True,
                name=f"unique_{name_collection.lower()}",
            )
            collection.create_index(
                [
                    (IPSourceBBIPField.LAYER.value, ASCENDING),
                ],
                name=f"layer_{name_collection.lower()}",
            )
        except CollectionInvalid as error:
            raise MongoCreateCollectionError(
                name_collection.value,
                error=f"La colección no es válida para creación\n{error}",
            )
        except Exception as error:
            raise MongoCreateCollectionError(name_collection.value, error=error)

    @staticmethod
    def delete(database: Database) -> None:
        name_collection = IPSourceBBIPCollection._NAME
        try:
            collection = database[name_collection]
            collection.delete_many({})
            collection.drop()
        except Exception as error:
            raise MongoDeleteCollectionError(name_collection, error=error)

    @staticmethod
    def export_data(
        database: Database,
        include_id: bool = False,
    ) -> None:
        name_collection = IPSourceBBIPCollection._NAME
        try:
            collection = database[name_collection]
            projection = {} if include_id else {"_id": 0}
            documents = collection.find({}, projection)

            data = (
                [MongoIPSourceBBIPDTO.from_mongo(doc) for doc in documents]
                if include_id
                else [MongoIPSourceBBIPDTO(**doc) for doc in documents]
            )

            writer = CSVWriter()
            writer.export(filename=IPSourceBBIPCollection._NAME, data=data)
        except Exception as error:
            raise MongoExportCollectionError(name_collection.value, error=error)

    @staticmethod
    def import_data(
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        name_collection = IPSourceBBIPCollection._NAME
        try:
            reader = IPSourceBBIPImport(delimiter)
            documents = reader.import_data(input_path)

            collection = database[name_collection]
            try:
                collection.insert_many(documents, ordered=False)
            except BulkWriteError as bwe:
                non_duplicate_errors = [
                    err
                    for err in bwe.details.get("writeErrors", [])
                    if err.get("code") != 11000  # E11000: duplicate key
                ]
                if non_duplicate_errors:
                    raise MongoImportCollectionError(name_collection, error=bwe)
        except FileEmptyError:
            return
        except DataContentError:
            raise
        except BulkWriteError:
            raise
        except Exception as error:
            raise MongoImportCollectionError(name_collection, error=error)
