import csv
from pathlib import Path
from bson import ObjectId
from pymongo import ASCENDING
from pymongo.database import Database
from pymongo.errors import CollectionInvalid
from scanbackup.shared import (
    MongoCreateCollectionError,
    MongoExportCollectionError,
    MongoImportCollectionError,
    MongoDeleteCollectionError,
    SCAN_COLLECTOR_SEPARATOR_FILE,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.records.bbip.traffic import (
    BBIPField,
    BBIP_TRAFFIC_SCHEMA,
)


class BBIPCollection:
    @staticmethod
    def create(name_collection: MongoCollectionName, database: Database) -> None:
        try:
            database.create_collection(
                name=name_collection, validator=BBIP_TRAFFIC_SCHEMA
            )
            collection = database[name_collection]
            collection.create_index(
                [
                    (BBIPField.DEVICE.value, ASCENDING),
                    (BBIPField.DATE.value, ASCENDING),
                    (BBIPField.TIME.value, ASCENDING),
                ],
                unique=True,
                name=f"unique_traffic_{name_collection.lower()}",
            )
            collection.create_index(
                [
                    (BBIPField.DATE.value, ASCENDING),
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
        output_path: Path,
        delimiter: str = SCAN_COLLECTOR_SEPARATOR_FILE,
        include_id: bool = False,
    ) -> None:
        try:
            collection = database[name_collection]
            projection = {} if include_id else {"_id": 0}
            documents = collection.find({}, projection)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", newline="", encoding="utf-8") as f:
                fields = (["_id"] if include_id else []) + [
                    field.value for field in BBIPField
                ]
                writer = csv.DictWriter(f, fieldnames=fields, delimiter=delimiter)
                writer.writeheader()
                for doc in documents:
                    doc[BBIPField.DEVICE.value] = str(doc[BBIPField.DEVICE.value])
                    if include_id:
                        doc["_id"] = str(doc["_id"])
                    writer.writerow(doc)
        except Exception as error:
            raise MongoExportCollectionError(name_collection.value, error=error)

    @staticmethod
    def import_data(
        name_collection: MongoCollectionName,
        database: Database,
        input_path: Path,
        delimiter: str = SCAN_COLLECTOR_SEPARATOR_FILE,
    ) -> None:
        try:
            collection = database[name_collection]
            with input_path.open("r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    row[BBIPField.DEVICE.value] = ObjectId(row[BBIPField.DEVICE.value])
                    if "_id" in row:
                        doc_id = ObjectId(row.pop("_id"))
                        collection.replace_one({"_id": doc_id}, row, upsert=True)
                    else:
                        collection.replace_one(
                            {
                                BBIPField.DEVICE.value: row[BBIPField.DEVICE.value],
                                BBIPField.DATE.value: row[BBIPField.DATE.value],
                                BBIPField.TIME.value: row[BBIPField.TIME.value],
                            },
                            row,
                            upsert=True,
                        )
        except Exception as error:
            raise MongoImportCollectionError(name_collection.value, error=error)
