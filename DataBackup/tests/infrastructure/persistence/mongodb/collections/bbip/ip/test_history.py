import unittest
from unittest.mock import MagicMock, patch
from pymongo.errors import CollectionInvalid
from scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.history import (
    IPHistoryBBIPCollection,
)
from scanbackup.shared import (
    MongoCreateCollectionError,
    MongoDeleteCollectionError,
    MongoImportCollectionError,
    FileEmptyError,
    DataContentError,
)

MODULE = "scanbackup.infrastructure.persistence.mongodb.collections.bbip.ip.history"


class TestIPHistoryBBIPCollectionCreate(unittest.TestCase):
    """Unit tests for IPHistoryBBIPCollection.create."""

    def test_creates_collection_and_indexes(self) -> None:
        """create() must create the collection and its two indexes."""
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        IPHistoryBBIPCollection.create("BORDE_IP_HISTORY_BBIP", database)

        database.create_collection.assert_called_once()
        self.assertEqual(collection.create_index.call_count, 2)

    def test_collection_invalid_wraps_error(self) -> None:
        """A CollectionInvalid error must be wrapped into MongoCreateCollectionError."""
        database = MagicMock()
        database.create_collection.side_effect = CollectionInvalid("bad schema")

        with self.assertRaises(MongoCreateCollectionError):
            IPHistoryBBIPCollection.create("BORDE_IP_HISTORY_BBIP", database)

    def test_generic_error_wraps_error(self) -> None:
        """Any other error must be wrapped into MongoCreateCollectionError."""
        database = MagicMock()
        database.create_collection.side_effect = RuntimeError("boom")

        with self.assertRaises(MongoCreateCollectionError):
            IPHistoryBBIPCollection.create("BORDE_IP_HISTORY_BBIP", database)


class TestIPHistoryBBIPCollectionDelete(unittest.TestCase):
    """Unit tests for IPHistoryBBIPCollection.delete."""

    def test_deletes_documents_and_drops_collection(self) -> None:
        """delete() must clear all documents and drop the collection."""
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        IPHistoryBBIPCollection.delete("BORDE_IP_HISTORY_BBIP", database)

        collection.delete_many.assert_called_once_with({})
        collection.drop.assert_called_once()

    def test_error_wraps_into_mongo_delete_error(self) -> None:
        """Any failure must be wrapped into MongoDeleteCollectionError."""
        database = MagicMock()
        database.__getitem__.side_effect = RuntimeError("boom")

        with self.assertRaises(MongoDeleteCollectionError):
            IPHistoryBBIPCollection.delete("BORDE_IP_HISTORY_BBIP", database)


class TestIPHistoryBBIPCollectionExportData(unittest.TestCase):
    """Unit tests for IPHistoryBBIPCollection.export_data."""

    @patch(f"{MODULE}.CSVWriter")
    def test_returns_the_writer_filepath(self, mock_writer_cls) -> None:
        """export_data() must return whatever CSVWriter.export returns."""
        database = MagicMock()
        collection = MagicMock()
        collection.find.return_value = [
            {
                "date": "2026-01-01",
                "time": "10:00:00",
                "in_prom": 1.0,
                "in_max": 2.0,
                "device": "Gi0/0/0",
            }
        ]
        database.__getitem__.return_value = collection
        mock_writer_cls.return_value.export.return_value = "/tmp/out.csv"

        result = IPHistoryBBIPCollection.export_data("BORDE_IP_HISTORY_BBIP", database)

        self.assertEqual(result, "/tmp/out.csv")

    @patch(f"{MODULE}.CSVWriter")
    def test_passes_dirpath_to_the_writer(self, mock_writer_cls) -> None:
        """export_data() must forward the given dirpath to CSVWriter."""
        from pathlib import Path

        database = MagicMock()
        collection = MagicMock()
        collection.find.return_value = []
        database.__getitem__.return_value = collection

        IPHistoryBBIPCollection.export_data(
            "BORDE_IP_HISTORY_BBIP", database, dirpath=Path("/tmp/out")
        )

        mock_writer_cls.assert_called_once_with(dir=Path("/tmp/out"))


class TestIPHistoryBBIPCollectionImportData(unittest.TestCase):
    """Unit tests for IPHistoryBBIPCollection.import_data."""

    @patch(f"{MODULE}.IPHistoryBBIPImport")
    def test_upserts_rows_without_id_by_device_date_time(self, mock_reader_cls) -> None:
        """A row without '_id' must be upserted using the device/date/time key."""
        mock_reader_cls.return_value.import_data.return_value = [
            {"id_source": "dev1", "date": "2026-01-01", "time": "10:00:00", "inProm": 1.0}
        ]
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        IPHistoryBBIPCollection.import_data(
            "BORDE_IP_HISTORY_BBIP", database, "/tmp/in.csv", ";"
        )

        collection.bulk_write.assert_called_once()
        operations = collection.bulk_write.call_args[0][0]
        self.assertEqual(len(operations), 1)

    @patch(f"{MODULE}.IPHistoryBBIPImport")
    def test_no_rows_skips_bulk_write(self, mock_reader_cls) -> None:
        """An empty row list must not trigger a bulk_write call."""
        mock_reader_cls.return_value.import_data.return_value = []
        database = MagicMock()
        collection = MagicMock()
        database.__getitem__.return_value = collection

        IPHistoryBBIPCollection.import_data(
            "BORDE_IP_HISTORY_BBIP", database, "/tmp/in.csv", ";"
        )

        collection.bulk_write.assert_not_called()

    @patch(f"{MODULE}.IPHistoryBBIPImport")
    def test_empty_file_is_silently_ignored(self, mock_reader_cls) -> None:
        """A FileEmptyError from the reader must be swallowed, not propagated."""
        mock_reader_cls.return_value.import_data.side_effect = FileEmptyError("/tmp/in.csv")
        database = MagicMock()

        IPHistoryBBIPCollection.import_data(
            "BORDE_IP_HISTORY_BBIP", database, "/tmp/in.csv", ";"
        )

    @patch(f"{MODULE}.IPHistoryBBIPImport")
    def test_data_content_error_is_propagated(self, mock_reader_cls) -> None:
        """A DataContentError from the reader must propagate unchanged."""
        mock_reader_cls.return_value.import_data.side_effect = DataContentError()
        database = MagicMock()

        with self.assertRaises(DataContentError):
            IPHistoryBBIPCollection.import_data(
                "BORDE_IP_HISTORY_BBIP", database, "/tmp/in.csv", ";"
            )

    @patch(f"{MODULE}.IPHistoryBBIPImport")
    def test_generic_error_wraps_into_mongo_import_error(self, mock_reader_cls) -> None:
        """Any other failure must be wrapped into MongoImportCollectionError."""
        mock_reader_cls.return_value.import_data.side_effect = RuntimeError("boom")
        database = MagicMock()

        with self.assertRaises(MongoImportCollectionError):
            IPHistoryBBIPCollection.import_data(
                "BORDE_IP_HISTORY_BBIP", database, "/tmp/in.csv", ";"
            )


if __name__ == "__main__":
    unittest.main()
