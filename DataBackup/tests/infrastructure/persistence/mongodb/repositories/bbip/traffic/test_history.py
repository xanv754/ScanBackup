import unittest
from unittest.mock import MagicMock, patch
from datetime import date, time
from bson import ObjectId
from pymongo.errors import BulkWriteError
from scanbackup.infrastructure.persistence.mongodb.repositories.bbip.traffic.history import (
    MongoTrafficHistoryBBIPRepository,
)
from scanbackup.domain import TrafficBBIPEntity
from scanbackup.shared import MongoInsertFailedError, MongoConnectionError

MODULE = "scanbackup.infrastructure.persistence.mongodb.repositories.bbip.traffic.history"


class TestMongoTrafficHistoryBBIPRepository(unittest.TestCase):
    """Unit tests for the MongoTrafficHistoryBBIPRepository."""

    def setUp(self) -> None:
        """Build a sample entity and repository instance for reuse across tests."""
        self.device_id = ObjectId()
        self.entity = TrafficBBIPEntity(
            date=date(2026, 1, 1),
            time=time(10, 0),
            in_prom=1.0,
            in_max=2.0,
            out_prom=1.5,
            out_max=2.5,
            device=self.device_id,
        )
        self.repository = MongoTrafficHistoryBBIPRepository("borde")

    def test_name_collection_is_built_from_layer_and_suffix(self) -> None:
        """The collection name must combine the uppercased layer and history suffix."""
        self.assertEqual(self.repository.name_collection, "BORDE_TRAFFIC_HISTORY_BBIP")

    def test_insert_with_no_data_is_a_no_op(self) -> None:
        """insert() with an empty list must not touch the database at all."""
        with patch(f"{MODULE}.MongoDatabase") as mock_client_cls:
            self.repository.insert([])
            mock_client_cls.assert_not_called()

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_insert_upserts_only_entities_with_valid_device(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """insert() must only bulk_write entities whose device exists in sources."""
        client = MagicMock()
        mock_client_cls.return_value = client
        sources_collection = MagicMock()
        sources_collection.find.return_value = [{"_id": self.device_id}]
        history_collection = MagicMock()
        client.get_connection.return_value.__getitem__.side_effect = [
            sources_collection,
            history_collection,
        ]

        self.repository.insert([self.entity])

        history_collection.bulk_write.assert_called_once()
        operations = history_collection.bulk_write.call_args[0][0]
        self.assertEqual(len(operations), 1)
        client.close_connection.assert_called_once()

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_insert_skips_entities_with_unknown_device(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """insert() must skip entities whose device is not a known source."""
        client = MagicMock()
        mock_client_cls.return_value = client
        sources_collection = MagicMock()
        sources_collection.find.return_value = []
        client.get_connection.return_value.__getitem__.return_value = sources_collection

        self.repository.insert([self.entity])

        client.close_connection.assert_called_once()

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_bulk_write_error_wraps_into_mongo_insert_failed(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """A BulkWriteError during bulk_write must be wrapped into MongoInsertFailedError."""
        client = MagicMock()
        mock_client_cls.return_value = client
        sources_collection = MagicMock()
        sources_collection.find.return_value = [{"_id": self.device_id}]
        history_collection = MagicMock()
        history_collection.bulk_write.side_effect = BulkWriteError({"writeErrors": []})
        client.get_connection.return_value.__getitem__.side_effect = [
            sources_collection,
            history_collection,
        ]

        with self.assertRaises(MongoInsertFailedError):
            self.repository.insert([self.entity])
        client.close_connection.assert_called_once()

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_mongo_connection_error_is_propagated(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """A MongoConnectionError while opening the connection must propagate unchanged."""
        client = MagicMock()
        mock_client_cls.return_value = client
        client.open_connection.side_effect = MongoConnectionError()

        with self.assertRaises(MongoConnectionError):
            self.repository.insert([self.entity])
        client.close_connection.assert_called_once()


if __name__ == "__main__":
    unittest.main()
