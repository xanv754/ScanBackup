from pathlib import Path
from bson import ObjectId
from pymongo import ASCENDING, ReplaceOne
from pymongo.database import Database
from pymongo.errors import CollectionInvalid
from scanbackup.shared import (
    FileEmptyError,
    MongoCreateCollectionError,
    MongoExportCollectionError,
    MongoImportCollectionError,
    MongoDeleteCollectionError,
    DataContentError,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.ip.active import (
    IPActiveBBIPField,
    IP_HISTORY_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections.operation import (
    CollectionOperation,
)
from scanbackup.infrastructure.readers import IPHistoryBBIPImport
from scanbackup.infrastructure.writers import CSVWriter
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.ip.history import (
    MongoIPHistoryBBIPDTO,
)


class IPHistoryBBIPCollection(CollectionOperation):
    @staticmethod
    def create(name_collection: MongoCollectionName, database: Database) -> None:
        try:
            database.create_collection(
                name=name_collection, validator=IP_HISTORY_SCHEMA
            )
            collection = database[name_collection]
            collection.create_index(
                [
                    (IPActiveBBIPField.DEVICE.value, ASCENDING),
                    (IPActiveBBIPField.DATE.value, ASCENDING),
                    (IPActiveBBIPField.TIME.value, ASCENDING),
                ],
                unique=True,
                name=f"unique_ip_{name_collection.lower()}",
            )
            collection.create_index(
                [
                    (IPActiveBBIPField.DATE.value, ASCENDING),
                ],
                name=f"date_ip_{name_collection.lower()}",
            )
        except CollectionInvalid as error:
            raise MongoCreateCollectionError(
                name_collection.value,
                error=f"La colección no es válida para creación\n{error}",
            )
        except Exception as error:
            raise MongoCreateCollectionError(name_collection.value, error=error)

    @staticmethod
    def delete(name_collection: MongoCollectionName, database: Database) -> None:
        try:
            collection = database[name_collection]
            collection.delete_many({})
            collection.drop()
        except Exception as error:
            raise MongoDeleteCollectionError(name_collection, error=error)

    @staticmethod
    def export_data(
        name_collection: MongoCollectionName,
        database: Database,
        include_id: bool = False,
    ) -> None:
        try:
            collection = database[name_collection]
            projection = {} if include_id else {"_id": 0}
            documents = collection.find({}, projection)

            data = (
                [MongoIPHistoryBBIPDTO.from_mongo(doc) for doc in documents]
                if include_id
                else [MongoIPHistoryBBIPDTO(**doc) for doc in documents]
            )

            writer = CSVWriter()
            writer.export(filename=name_collection, data=data)
        except Exception as error:
            raise MongoExportCollectionError(name_collection.value, error=error)

    @staticmethod
    def import_data(
        name_collection: MongoCollectionName,
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        try:
            collection = database[name_collection]
            reader = IPHistoryBBIPImport(delimiter)
            rows = reader.import_data(input_path)

            operations = []
            for row in rows:
                if "_id" in row:
                    doc_id = ObjectId(row.pop("_id"))
                    operations.append(ReplaceOne({"_id": doc_id}, row, upsert=True))
                else:
                    operations.append(
                        ReplaceOne(
                            {
                                IPActiveBBIPField.DEVICE.value: row[
                                    IPActiveBBIPField.DEVICE.value
                                ],
                                IPActiveBBIPField.DATE.value: row[
                                    IPActiveBBIPField.DATE.value
                                ],
                                IPActiveBBIPField.TIME.value: row[
                                    IPActiveBBIPField.TIME.value
                                ],
                            },
                            row,
                            upsert=True,
                        )
                    )
            if operations:
                collection.bulk_write(operations, ordered=False)
        except DataContentError:
            raise
        except FileEmptyError:
            return
        except DataContentError:
            raise
        except Exception as error:
            raise MongoImportCollectionError(name_collection.value, error=error)
