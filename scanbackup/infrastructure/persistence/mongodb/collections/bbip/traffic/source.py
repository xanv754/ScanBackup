import csv
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
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.source import (
    BBIPSourceField,
    SOURCE_TRAFFIC_BBIP_SCHEMA,
)


class BBIPSourceCollection:
    _NAME = MongoCollectionName.BBIP_SOURCES.value

    @staticmethod
    def create(database: Database) -> None:
        name_collection = BBIPSourceCollection._NAME
        try:
            database.create_collection(
                name=name_collection, validator=SOURCE_TRAFFIC_BBIP_SCHEMA
            )
            collection = database[name_collection]
            collection.create_index(
                [
                    (BBIPSourceField.LAYER.value, ASCENDING),
                    (BBIPSourceField.TYPE.value, ASCENDING),
                    (BBIPSourceField.INTERFACE.value, ASCENDING),
                ],
                unique=True,
                name=f"unique_{name_collection.lower()}",
            )
            collection.create_index(
                [
                    (BBIPSourceField.LAYER.value, ASCENDING),
                ],
                name=f"layer_{name_collection.lower()}",
            )
        except CollectionInvalid as error:
            raise MongoCreateCollectionError(
                name_collection,
                error=f"La colección no es válida para creación\n{error}",
            )
        except Exception as error:
            raise MongoCreateCollectionError(name_collection, error=error)

    @staticmethod
    def delete(database: Database) -> None:
        name_collection = BBIPSourceCollection._NAME
        try:
            collection = database[name_collection]
            collection.delete_many({})
            collection.drop()
        except Exception as error:
            raise MongoDeleteCollectionError(name_collection, error=error)

    @staticmethod
    def export_data(
        database: Database,
        output_path: Path,
        delimiter: str,
        include_id: bool = False,
    ) -> None:
        name_collection = BBIPSourceCollection._NAME
        try:
            collection = database[name_collection]
            projection = {} if include_id else {"_id": 0}
            documents = collection.find({}, projection)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", newline="", encoding="utf-8") as f:
                fields = (["_id"] if include_id else []) + [
                    field.value for field in BBIPSourceField
                ]
                writer = csv.DictWriter(f, fieldnames=fields, delimiter=delimiter)
                writer.writeheader()
                for doc in documents:
                    if include_id:
                        doc["_id"] = str(doc["_id"])
                    writer.writerow(doc)
        except Exception as error:
            raise MongoExportCollectionError(name_collection, error=error)

    @staticmethod
    def import_data(
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        name_collection = BBIPSourceCollection._NAME
        total_neccesary_col = len(BBIPSourceField)
        try:
            collection = database[name_collection]
            documents = []
            with input_path.open("r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for i, row in enumerate(reader, start=1):
                    document = {k: v for k, v in row.items() if k != "_id"}
                    if len(document) != total_neccesary_col:
                        raise DataContentError(
                            extra_msg=f"Columnas faltantes en la línea {i}"
                        )
                    try:
                        document[BBIPSourceField.CAPACITY.value] = float(
                            document[BBIPSourceField.CAPACITY.value]
                        )
                    except (ValueError, KeyError):
                        raise DataContentError(
                            extra_msg=f"Valor inválido de capacidad, línea {i}"
                        )
                    documents.append(document)

            if not documents:
                raise FileEmptyError(filepath=input_path)

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
        except MongoImportCollectionError:
            raise
        except Exception as error:
            raise MongoImportCollectionError(name_collection, error=error)
