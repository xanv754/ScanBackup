from pathlib import Path
from typing import Any

from bson import ObjectId
from pymongo import ReplaceOne
from pymongo.database import Database
from pymongo.errors import BulkWriteError, CollectionInvalid

from scanbackup.shared import (
    DataContentError,
    FileEmptyError,
    MongoCreateCollectionError,
    MongoDeleteCollectionError,
    MongoExportCollectionError,
    MongoImportCollectionError,
)

IndexSpec = tuple[list[tuple[str, int]], bool, str]
"""A single `create_index` call: (fields, unique, index_name)."""


def create_collection(
    name: str,
    database: Database,
    schema: dict[str, Any],
    indexes: tuple[IndexSpec, ...],
) -> None:
    """Create `name` with its JSON schema validator and every index in `indexes`."""
    try:
        database.create_collection(name=name, validator=schema)
        collection = database[name]
        for fields, unique, index_name in indexes:
            collection.create_index(fields, unique=unique, name=index_name)
    except CollectionInvalid as error:
        raise MongoCreateCollectionError(
            name, error=f"La colección no es válida para creación\n{error}"
        )
    except Exception as error:
        raise MongoCreateCollectionError(name, error=error)


def delete_collection(name: str, database: Database) -> None:
    """Delete every document in `name` and drop the collection."""
    try:
        collection = database[name]
        collection.delete_many({})
        collection.drop()
    except Exception as error:
        raise MongoDeleteCollectionError(name, error=error)


def export_collection(
    name: str,
    database: Database,
    dto_cls: type,
    writer_cls: type,
    dirpath: Path | None = None,
    include_id: bool = False,
) -> str:
    """Export every document in `name` as `dto_cls` rows through `writer_cls`."""
    try:
        collection = database[name]
        projection = {} if include_id else {"_id": 0}
        documents = collection.find({}, projection)

        data = (
            [dto_cls.from_mongo(doc) for doc in documents]
            if include_id
            else [dto_cls(**doc) for doc in documents]
        )

        writer = writer_cls(dir=dirpath)
        return writer.export(filename=name, data=data, model=dto_cls)
    except Exception as error:
        raise MongoExportCollectionError(name, error=error)


def import_upsert_by_key(
    name: str,
    database: Database,
    reader_cls: type,
    input_path: Path,
    delimiter: str | None,
    key_fields: tuple[str, ...],
) -> None:
    """Upsert every row from `reader_cls`, by `_id` when present, else by `key_fields`."""
    try:
        reader = reader_cls(delimiter)
        rows = reader.import_data(input_path)

        operations = []
        for row in rows:
            if "_id" in row:
                doc_id = ObjectId(row.pop("_id"))
                operations.append(ReplaceOne({"_id": doc_id}, row, upsert=True))
            else:
                key = {field: row[field] for field in key_fields}
                operations.append(ReplaceOne(key, row, upsert=True))

        if operations:
            database[name].bulk_write(operations, ordered=False)
    except FileEmptyError:
        return
    except DataContentError:
        raise
    except Exception as error:
        raise MongoImportCollectionError(name, error=error)


def import_insert_many(
    name: str,
    database: Database,
    reader_cls: type,
    input_path: Path,
    delimiter: str,
) -> None:
    """Insert every row from `reader_cls`, tolerating duplicate-key (E11000) errors."""
    try:
        reader = reader_cls(delimiter)
        documents = reader.import_data(input_path)

        collection = database[name]
        try:
            collection.insert_many(documents, ordered=False)
        except BulkWriteError as bwe:
            non_duplicate_errors = [
                err
                for err in bwe.details.get("writeErrors", [])
                if err.get("code") != 11000  # E11000: duplicate key
            ]
            if non_duplicate_errors:
                raise MongoImportCollectionError(name, error=bwe)
    except DataContentError:
        raise
    except FileEmptyError:
        return
    except MongoImportCollectionError:
        raise
    except Exception as error:
        raise MongoImportCollectionError(name, error=error)
