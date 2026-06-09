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
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.data import (
    TrafficBBIPField,
    BBIP_TRAFFIC_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections.operation import (
    CollectionOperation,
)
from scanbackup.infrastructure.readers import (
    TrafficHistoryBBIPImport,
)
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.history import (
    MongoTrafficHistoryBBIPDTO,
)
from scanbackup.infrastructure.writers import CSVWriter


class TrafficHistoryBBIPCollection(CollectionOperation):
    @staticmethod
    def create(name_collection: MongoCollectionName, database: Database) -> None:
        try:
            database.create_collection(
                name=name_collection, validator=BBIP_TRAFFIC_SCHEMA
            )
            collection = database[name_collection]
            collection.create_index(
                [
                    (TrafficBBIPField.DEVICE.value, ASCENDING),
                    (TrafficBBIPField.DATE.value, ASCENDING),
                    (TrafficBBIPField.TIME.value, ASCENDING),
                ],
                unique=True,
                name=f"unique_traffic_{name_collection.lower()}",
            )
            collection.create_index(
                [
                    (TrafficBBIPField.DATE.value, ASCENDING),
                ],
                name=f"date_traffic_{name_collection.lower()}",
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
                [MongoTrafficHistoryBBIPDTO.from_mongo(doc) for doc in documents]
                if include_id
                else [MongoTrafficHistoryBBIPDTO(**doc) for doc in documents]
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
        delimiter: str | None = None,
    ) -> None:
        try:
            reader = TrafficHistoryBBIPImport(delimiter)
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
                                TrafficBBIPField.DEVICE.value: row[
                                    TrafficBBIPField.DEVICE.value
                                ],
                                TrafficBBIPField.DATE.value: row[
                                    TrafficBBIPField.DATE.value
                                ],
                                TrafficBBIPField.TIME.value: row[
                                    TrafficBBIPField.TIME.value
                                ],
                            },
                            row,
                            upsert=True,
                        )
                    )

            if operations:
                collection = database[name_collection]
                collection.bulk_write(operations)
        except FileEmptyError:
            return
        except DataContentError:
            raise
        except Exception as error:
            raise MongoImportCollectionError(name_collection.value, error=error)
