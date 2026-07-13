import unittest
from unittest.mock import MagicMock, patch
from pymongo.errors import BulkWriteError, CollectionInvalid
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.source import (
    IPSourceBBIPCollection,
)
from scanbackup.shared import (
    MongoCreateCollectionError,
    MongoDeleteCollectionError,
    MongoImportCollectionError,
    FileEmptyError,
    DataContentError,
)

MODULE = "scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.source"


class TestIPSourceBBIPCollectionCreate(unittest.TestCase):
    """Unit tests for IPSourceBBIPCollection.create."""

    def test_creates_collection_and_indexes(self) -> None:
        """create() must create the collection and its two indexes."""
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        IPSourceBBIPCollection.create(database)

        database.create_collection.assert_called_once()
        self.assertEqual(collection.create_index.call_count, 2)

    def test_collection_invalid_wraps_error(self) -> None:
        """A CollectionInvalid error must be wrapped into MongoCreateCollectionError."""
        database = MagicMock()
        database.create_collection.side_effect = CollectionInvalid("bad schema")

        with self.assertRaises(MongoCreateCollectionError):
            IPSourceBBIPCollection.create(database)


class TestIPSourceBBIPCollectionDelete(unittest.TestCase):
    """Unit tests for IPSourceBBIPCollection.delete."""

    def test_deletes_documents_and_drops_collection(self) -> None:
        """delete() must clear all documents and drop the collection."""
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        IPSourceBBIPCollection.delete(database)

        collection.delete_many.assert_called_once_with({})
        collection.drop.assert_called_once()

    def test_error_wraps_into_mongo_delete_error(self) -> None:
        """Any failure must be wrapped into MongoDeleteCollectionError."""
        database = MagicMock()
        database.__getitem__.side_effect = RuntimeError("boom")

        with self.assertRaises(MongoDeleteCollectionError):
            IPSourceBBIPCollection.delete(database)


class TestIPSourceBBIPCollectionExportData(unittest.TestCase):
    """Unit tests for IPSourceBBIPCollection.export_data."""

    @patch(f"{MODULE}.CSVWriter")
    def test_returns_the_writer_filepath(self, mock_writer_cls) -> None:
        """export_data() must return whatever CSVWriter.export returns."""
        database = MagicMock()
        collection = MagicMock()
        collection.find.return_value = [
            {"link": "http://example.com", "interface": "Gi0/0/0", "status": "ACTIVO", "layer": "DINT"}
        ]
        database.__getitem__.return_value = collection
        mock_writer_cls.return_value.export.return_value = "/tmp/out.csv"

        result = IPSourceBBIPCollection.export_data(database)

        self.assertEqual(result, "/tmp/out.csv")

    @patch(f"{MODULE}.CSVWriter")
    def test_include_id_uses_from_mongo(self, mock_writer_cls) -> None:
        """When include_id=True the documents must be mapped through from_mongo."""
        database = MagicMock()
        collection = MagicMock()
        collection.find.return_value = [
            {
                "_id": "abc123",
                "link": "http://example.com",
                "interface": "Gi0/0/0",
                "status": "ACTIVO",
                "layer": "DINT",
            }
        ]
        database.__getitem__.return_value = collection
        mock_writer_cls.return_value.export.return_value = "/tmp/out.csv"

        IPSourceBBIPCollection.export_data(database, include_id=True)

        exported_data = mock_writer_cls.return_value.export.call_args.kwargs["data"]
        self.assertEqual(exported_data[0].id, "abc123")

    @patch(f"{MODULE}.CSVWriter")
    def test_passes_dirpath_to_the_writer(self, mock_writer_cls) -> None:
        """export_data() must forward the given dirpath to CSVWriter."""
        from pathlib import Path

        database = MagicMock()
        collection = MagicMock()
        collection.find.return_value = []
        database.__getitem__.return_value = collection

        IPSourceBBIPCollection.export_data(database, dirpath=Path("/tmp/out"))

        mock_writer_cls.assert_called_once_with(dir=Path("/tmp/out"))


class TestIPSourceBBIPCollectionImportData(unittest.TestCase):
    """Unit tests for IPSourceBBIPCollection.import_data."""

    @patch(f"{MODULE}.IPSourceBBIPImport")
    def test_inserts_documents_from_reader(self, mock_reader_cls) -> None:
        """import_data() must insert every document returned by the reader."""
        mock_reader_cls.return_value.import_data.return_value = [{"a": 1}]
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        IPSourceBBIPCollection.import_data(database, "/tmp/in.csv", ";")

        collection.insert_many.assert_called_once_with([{"a": 1}], ordered=False)

    @patch(f"{MODULE}.IPSourceBBIPImport")
    def test_empty_file_is_silently_ignored(self, mock_reader_cls) -> None:
        """A FileEmptyError from the reader must be swallowed, not propagated."""
        mock_reader_cls.return_value.import_data.side_effect = FileEmptyError("/tmp/in.csv")
        database = MagicMock()

        IPSourceBBIPCollection.import_data(database, "/tmp/in.csv", ";")

    @patch(f"{MODULE}.IPSourceBBIPImport")
    def test_data_content_error_is_propagated(self, mock_reader_cls) -> None:
        """A DataContentError from the reader must propagate unchanged."""
        mock_reader_cls.return_value.import_data.side_effect = DataContentError()
        database = MagicMock()

        with self.assertRaises(DataContentError):
            IPSourceBBIPCollection.import_data(database, "/tmp/in.csv", ";")

    @patch(f"{MODULE}.IPSourceBBIPImport")
    def test_duplicate_key_errors_are_ignored(self, mock_reader_cls) -> None:
        """A BulkWriteError containing only duplicate-key errors must not raise."""
        mock_reader_cls.return_value.import_data.return_value = [{"a": 1}]
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection
        collection.insert_many.side_effect = BulkWriteError(
            {"writeErrors": [{"code": 11000}]}
        )

        IPSourceBBIPCollection.import_data(database, "/tmp/in.csv", ";")

    @patch(f"{MODULE}.IPSourceBBIPImport")
    def test_non_duplicate_bulk_errors_raise(self, mock_reader_cls) -> None:
        """A BulkWriteError with non-duplicate errors must raise MongoImportCollectionError."""
        mock_reader_cls.return_value.import_data.return_value = [{"a": 1}]
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection
        collection.insert_many.side_effect = BulkWriteError(
            {"writeErrors": [{"code": 12345}]}
        )

        with self.assertRaises(MongoImportCollectionError):
            IPSourceBBIPCollection.import_data(database, "/tmp/in.csv", ";")


if __name__ == "__main__":
    unittest.main()
