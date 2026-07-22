import unittest
from pathlib import Path
from unittest.mock import MagicMock
from bson import ObjectId
from pymongo import ASCENDING
from pymongo.errors import BulkWriteError, CollectionInvalid
from scanbackup.infrastructure.persistence.mongodb.collections import mongo_io
from scanbackup.shared import (
    DataContentError,
    FileEmptyError,
    MongoCreateCollectionError,
    MongoDeleteCollectionError,
    MongoExportCollectionError,
    MongoImportCollectionError,
)


class TestCreateCollection(unittest.TestCase):
    """Unit tests for mongo_io.create_collection."""

    def test_creates_collection_and_every_index(self) -> None:
        """create_collection() must create the collection and each index in indexes."""
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection
        indexes = (
            ([("device", ASCENDING)], True, "unique_idx"),
            ([("date", ASCENDING)], False, "date_idx"),
        )

        mongo_io.create_collection("NAME", database, {"schema": True}, indexes)

        database.create_collection.assert_called_once_with(
            name="NAME", validator={"schema": True}
        )
        self.assertEqual(collection.create_index.call_count, 2)
        collection.create_index.assert_any_call(
            [("device", ASCENDING)], unique=True, name="unique_idx"
        )
        collection.create_index.assert_any_call(
            [("date", ASCENDING)], unique=False, name="date_idx"
        )

    def test_collection_invalid_wraps_into_mongo_create_error(self) -> None:
        """A CollectionInvalid error must be wrapped into MongoCreateCollectionError."""
        database = MagicMock()
        database.create_collection.side_effect = CollectionInvalid("bad schema")

        with self.assertRaises(MongoCreateCollectionError):
            mongo_io.create_collection("NAME", database, {}, ())

    def test_generic_error_wraps_into_mongo_create_error(self) -> None:
        """Any other failure must be wrapped into MongoCreateCollectionError."""
        database = MagicMock()
        database.create_collection.side_effect = RuntimeError("boom")

        with self.assertRaises(MongoCreateCollectionError):
            mongo_io.create_collection("NAME", database, {}, ())


class TestDeleteCollection(unittest.TestCase):
    """Unit tests for mongo_io.delete_collection."""

    def test_deletes_documents_and_drops_collection(self) -> None:
        """delete_collection() must clear all documents and drop the collection."""
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        mongo_io.delete_collection("NAME", database)

        collection.delete_many.assert_called_once_with({})
        collection.drop.assert_called_once()

    def test_error_wraps_into_mongo_delete_error(self) -> None:
        """Any failure must be wrapped into MongoDeleteCollectionError."""
        database = MagicMock()
        database.__getitem__.side_effect = RuntimeError("boom")

        with self.assertRaises(MongoDeleteCollectionError):
            mongo_io.delete_collection("NAME", database)


class TestExportCollection(unittest.TestCase):
    """Unit tests for mongo_io.export_collection."""

    def test_include_id_false_builds_rows_with_dto_cls_constructor(self) -> None:
        """When include_id is False, rows must be built via dto_cls(**doc) without _id."""
        database = MagicMock()
        collection = MagicMock()
        collection.find.return_value = [{"device": "Gi0/0/0"}]
        database.__getitem__.return_value = collection

        dto_cls = MagicMock()
        writer_cls = MagicMock()
        writer_cls.return_value.export.return_value = "/tmp/out.csv"

        result = mongo_io.export_collection(
            "NAME", database, dto_cls, writer_cls, include_id=False
        )

        collection.find.assert_called_once_with({}, {"_id": 0})
        dto_cls.assert_called_once_with(device="Gi0/0/0")
        dto_cls.from_mongo.assert_not_called()
        self.assertEqual(result, "/tmp/out.csv")

    def test_include_id_true_builds_rows_with_from_mongo(self) -> None:
        """When include_id is True, rows must be built via dto_cls.from_mongo(doc)."""
        database = MagicMock()
        collection = MagicMock()
        doc = {"_id": ObjectId(), "device": "Gi0/0/0"}
        collection.find.return_value = [doc]
        database.__getitem__.return_value = collection

        dto_cls = MagicMock()
        writer_cls = MagicMock()

        mongo_io.export_collection(
            "NAME", database, dto_cls, writer_cls, include_id=True
        )

        collection.find.assert_called_once_with({}, {})
        dto_cls.from_mongo.assert_called_once_with(doc)
        dto_cls.assert_not_called()

    def test_passes_filename_data_and_model_to_the_writer(self) -> None:
        """export_collection() must call writer.export with filename, data, and model."""
        database = MagicMock()
        collection = MagicMock()
        collection.find.return_value = []
        database.__getitem__.return_value = collection

        dto_cls = MagicMock()
        writer_cls = MagicMock()
        writer = writer_cls.return_value

        mongo_io.export_collection(
            "NAME", database, dto_cls, writer_cls, dirpath=Path("/tmp/out")
        )

        writer_cls.assert_called_once_with(dir=Path("/tmp/out"))
        writer.export.assert_called_once_with(filename="NAME", data=[], model=dto_cls)

    def test_error_wraps_into_mongo_export_error(self) -> None:
        """Any failure must be wrapped into MongoExportCollectionError."""
        database = MagicMock()
        database.__getitem__.side_effect = RuntimeError("boom")

        with self.assertRaises(MongoExportCollectionError):
            mongo_io.export_collection("NAME", database, MagicMock(), MagicMock())


class TestImportUpsertByKey(unittest.TestCase):
    """Unit tests for mongo_io.import_upsert_by_key."""

    def test_row_with_id_upserts_by_id(self) -> None:
        """A row with '_id' must be upserted via ReplaceOne filtered by _id."""
        object_id = ObjectId()
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.return_value = [
            {"_id": str(object_id), "device": "Gi0/0/0"}
        ]
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        mongo_io.import_upsert_by_key(
            "NAME", database, reader_cls, Path("/tmp/in.csv"), ";", ("device",)
        )

        collection.bulk_write.assert_called_once()
        operations = collection.bulk_write.call_args[0][0]
        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0]._filter, {"_id": object_id})
        self.assertEqual(operations[0]._doc, {"device": "Gi0/0/0"})
        self.assertTrue(collection.bulk_write.call_args[1]["ordered"] is False)

    def test_row_without_id_upserts_by_key_fields(self) -> None:
        """A row without '_id' must be upserted via ReplaceOne filtered by key_fields."""
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.return_value = [
            {"device": "Gi0/0/0", "date": "2026-01-01", "in_prom": 1.0}
        ]
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        mongo_io.import_upsert_by_key(
            "NAME", database, reader_cls, Path("/tmp/in.csv"), ";", ("device", "date")
        )

        collection.bulk_write.assert_called_once()
        operations = collection.bulk_write.call_args[0][0]
        self.assertEqual(len(operations), 1)
        self.assertEqual(
            operations[0]._filter, {"device": "Gi0/0/0", "date": "2026-01-01"}
        )
        self.assertEqual(
            operations[0]._doc,
            {"device": "Gi0/0/0", "date": "2026-01-01", "in_prom": 1.0},
        )

    def test_no_rows_skips_bulk_write(self) -> None:
        """An empty row list must not trigger a bulk_write call."""
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.return_value = []
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        mongo_io.import_upsert_by_key(
            "NAME", database, reader_cls, Path("/tmp/in.csv"), ";", ("device",)
        )

        collection.bulk_write.assert_not_called()

    def test_empty_file_is_silently_ignored(self) -> None:
        """A FileEmptyError from the reader must be swallowed, not propagated."""
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.side_effect = FileEmptyError("/tmp/in.csv")
        database = MagicMock()

        mongo_io.import_upsert_by_key(
            "NAME", database, reader_cls, Path("/tmp/in.csv"), ";", ("device",)
        )

    def test_data_content_error_is_propagated(self) -> None:
        """A DataContentError from the reader must propagate unchanged."""
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.side_effect = DataContentError()
        database = MagicMock()

        with self.assertRaises(DataContentError):
            mongo_io.import_upsert_by_key(
                "NAME", database, reader_cls, Path("/tmp/in.csv"), ";", ("device",)
            )

    def test_generic_error_wraps_into_mongo_import_error(self) -> None:
        """Any other failure must be wrapped into MongoImportCollectionError."""
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.side_effect = RuntimeError("boom")
        database = MagicMock()

        with self.assertRaises(MongoImportCollectionError):
            mongo_io.import_upsert_by_key(
                "NAME", database, reader_cls, Path("/tmp/in.csv"), ";", ("device",)
            )


class TestImportInsertMany(unittest.TestCase):
    """Unit tests for mongo_io.import_insert_many."""

    def test_inserts_documents_from_reader(self) -> None:
        """import_insert_many() must insert every document returned by the reader."""
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.return_value = [{"a": 1}]
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        mongo_io.import_insert_many("NAME", database, reader_cls, Path("/tmp/in.csv"), ";")

        collection.insert_many.assert_called_once_with([{"a": 1}], ordered=False)

    def test_duplicate_key_errors_are_tolerated(self) -> None:
        """A BulkWriteError whose only errors are code 11000 must not raise."""
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.return_value = [{"a": 1}]
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection
        collection.insert_many.side_effect = BulkWriteError(
            {"writeErrors": [{"code": 11000}]}
        )

        mongo_io.import_insert_many("NAME", database, reader_cls, Path("/tmp/in.csv"), ";")

    def test_non_duplicate_bulk_errors_raise_mongo_import_error(self) -> None:
        """A BulkWriteError with non-duplicate errors must raise MongoImportCollectionError."""
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.return_value = [{"a": 1}]
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection
        collection.insert_many.side_effect = BulkWriteError(
            {"writeErrors": [{"code": 12345}]}
        )

        with self.assertRaises(MongoImportCollectionError):
            mongo_io.import_insert_many(
                "NAME", database, reader_cls, Path("/tmp/in.csv"), ";"
            )

    def test_empty_file_is_silently_ignored(self) -> None:
        """A FileEmptyError from the reader must be swallowed, not propagated."""
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.side_effect = FileEmptyError("/tmp/in.csv")
        database = MagicMock()

        mongo_io.import_insert_many("NAME", database, reader_cls, Path("/tmp/in.csv"), ";")

    def test_data_content_error_is_propagated(self) -> None:
        """A DataContentError from the reader must propagate unchanged."""
        reader_cls = MagicMock()
        reader_cls.return_value.import_data.side_effect = DataContentError()
        database = MagicMock()

        with self.assertRaises(DataContentError):
            mongo_io.import_insert_many(
                "NAME", database, reader_cls, Path("/tmp/in.csv"), ";"
            )


if __name__ == "__main__":
    unittest.main()
