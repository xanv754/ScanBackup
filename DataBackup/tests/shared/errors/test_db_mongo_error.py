import unittest
from unittest.mock import patch
from scanbackup.shared.errors.db_mongo_error import (
    MongoDatabaseError,
    MongoCollectionNotFoundError,
    MongoCreateCollectionError,
    MongoExportCollectionError,
    MongoImportCollectionError,
    MongoDeleteCollectionError,
    MongoConnectionError,
    MongoInsertFailedError,
    MongoGetFailedError,
)


@patch("scanbackup.shared.errors.system.Terminal")
@patch("scanbackup.shared.errors.system.Log")
class TestDbMongoError(unittest.TestCase):
    """Unit tests for the MongoDB error hierarchy."""

    def test_mongo_database_error_default_message(self, mock_log, mock_terminal) -> None:
        """MongoDatabaseError without a message must use the default text."""
        error = MongoDatabaseError()
        self.assertIn("operación", str(error))

    def test_collection_not_found_includes_name(self, mock_log, mock_terminal) -> None:
        """MongoCollectionNotFoundError must include the collection name."""
        error = MongoCollectionNotFoundError("TRAFFIC_SOURCE_BBIP")
        self.assertIn("TRAFFIC_SOURCE_BBIP", str(error))

    def test_create_collection_error_includes_name(self, mock_log, mock_terminal) -> None:
        """MongoCreateCollectionError must include the collection name."""
        error = MongoCreateCollectionError("IP_SOURCE_BBIP")
        self.assertIn("IP_SOURCE_BBIP", str(error))

    def test_export_collection_error_includes_name(self, mock_log, mock_terminal) -> None:
        """MongoExportCollectionError must include the collection name."""
        error = MongoExportCollectionError("TRAFFIC_SOURCE_BBIP")
        self.assertIn("TRAFFIC_SOURCE_BBIP", str(error))

    def test_export_collection_error_appends_extra_msg(self, mock_log, mock_terminal) -> None:
        """MongoExportCollectionError must append the extra message when provided."""
        error = MongoExportCollectionError("TRAFFIC_SOURCE_BBIP", extra_msg="disco lleno")
        self.assertIn("disco lleno", str(error))

    def test_import_collection_error_includes_name(self, mock_log, mock_terminal) -> None:
        """MongoImportCollectionError must include the collection name."""
        error = MongoImportCollectionError("BORDE_TRAFFIC_HISTORY_BBIP")
        self.assertIn("BORDE_TRAFFIC_HISTORY_BBIP", str(error))

    def test_delete_collection_error_includes_name(self, mock_log, mock_terminal) -> None:
        """MongoDeleteCollectionError must include the collection name."""
        error = MongoDeleteCollectionError("BORDE_TRAFFIC_HISTORY_BBIP")
        self.assertIn("BORDE_TRAFFIC_HISTORY_BBIP", str(error))

    def test_connection_error_appends_extra_msg(self, mock_log, mock_terminal) -> None:
        """MongoConnectionError must append the extra message when provided."""
        error = MongoConnectionError(extra_msg="timeout")
        self.assertIn("timeout", str(error))

    def test_insert_failed_error_appends_extra_msg(self, mock_log, mock_terminal) -> None:
        """MongoInsertFailedError must append the extra message when provided."""
        error = MongoInsertFailedError(extra_msg="bulk fallido")
        self.assertIn("bulk fallido", str(error))

    def test_get_failed_error_includes_error(self, mock_log, mock_terminal) -> None:
        """MongoGetFailedError must include the wrapped error text."""
        error = MongoGetFailedError(name_collection="TRAFFIC_SOURCE_BBIP", error="boom")
        self.assertIn("boom", str(error))

    def test_get_failed_error_includes_collection_name(self, mock_log, mock_terminal) -> None:
        """MongoGetFailedError must include the collection name in its own message."""
        error = MongoGetFailedError(name_collection="TRAFFIC_SOURCE_BBIP")
        self.assertIn("TRAFFIC_SOURCE_BBIP", str(error))

    def test_get_failed_error_appends_extra_msg(self, mock_log, mock_terminal) -> None:
        """MongoGetFailedError must append the extra message when provided."""
        error = MongoGetFailedError(name_collection="TRAFFIC_SOURCE_BBIP", extra_msg="timeout")
        self.assertIn("timeout", str(error))


if __name__ == "__main__":
    unittest.main()
