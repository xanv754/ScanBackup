import csv
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
        output_path: Path,
        delimiter: str,
        include_id: bool = False,
    ) -> None:
        try:
            collection = database[name_collection]
            projection = {} if include_id else {"_id": 0}
            documents = collection.find({}, projection)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", newline="", encoding="utf-8") as f:
                fields = (["_id"] if include_id else []) + [
                    field.value for field in IPActiveBBIPField
                ]
                writer = csv.DictWriter(f, fieldnames=fields, delimiter=delimiter)
                writer.writeheader()
                for doc in documents:
                    doc[IPActiveBBIPField.DEVICE.value] = str(
                        doc[IPActiveBBIPField.DEVICE.value]
                    )
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
        delimiter: str,
    ) -> None:
        try:
            total_neccesary_col = len(IPActiveBBIPField)
            collection = database[name_collection]

            if input_path.stat().st_size == 0:
                raise FileEmptyError(filepath=input_path)

            operations = []
            with input_path.open("r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for i, row in enumerate(reader, start=1):
                    total_columns = len(row)
                    if (
                        total_columns < total_neccesary_col
                        or total_columns > total_neccesary_col + 1
                    ):
                        raise DataContentError(
                            extra_msg=f"Total de columnas inválido en la línea {i}"
                        )

                    try:
                        row[IPActiveBBIPField.DEVICE.value] = ObjectId(
                            row[IPActiveBBIPField.DEVICE.value]
                        )
                    except (ValueError, KeyError):
                        raise DataContentError(
                            extra_msg=f"Valor inválido de id, línea {i}"
                        )

                    try:
                        row[IPActiveBBIPField.IN_MAX] = float(
                            row[IPActiveBBIPField.IN_MAX.value]
                        )
                    except (ValueError, KeyError):
                        raise DataContentError(
                            extra_msg=f"Valor inválido de in max, línea {i}"
                        )

                    try:
                        row[IPActiveBBIPField.IN_PROM] = float(
                            row[IPActiveBBIPField.IN_PROM.value]
                        )
                    except (ValueError, KeyError):
                        raise DataContentError(
                            extra_msg=f"Valor inválido de in prom, línea {i}"
                        )

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
        except FileEmptyError:
            return
        except DataContentError:
            raise
        except Exception as error:
            raise MongoImportCollectionError(name_collection.value, error=error)
