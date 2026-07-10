import unittest
from unittest.mock import MagicMock, patch
from datetime import date
from bson import ObjectId
from pymongo.errors import BulkWriteError
from scanbackup.infrastructure.persistence.mongodb.repositories.bbip.traffic.summaries.daily import (
    MongoTrafficDailySummaryBBIPRepository,
)
from scanbackup.domain import TrafficDailySummaryBBIPEntity
from scanbackup.shared import MongoInsertFailedError, MongoConnectionError

MODULE = (
    "scanbackup.infrastructure.persistence.mongodb.repositories.bbip.traffic.summaries.daily"
)


class TestMongoTrafficDailySummaryBBIPRepository(unittest.TestCase):
    """Unit tests for the MongoTrafficDailySummaryBBIPRepository."""

    def setUp(self) -> None:
        """Build a repository instance and a sample entity for reuse across tests."""
        self.repository = MongoTrafficDailySummaryBBIPRepository()
        self.entity = TrafficDailySummaryBBIPEntity(
            date=date(2026, 1, 1),
            in_prom=1.0,
            in_max=2.0,
            out_prom=1.5,
            out_max=2.5,
            use=80.0,
            device=ObjectId(),
        )

    def test_insert_with_no_data_is_a_no_op(self) -> None:
        """insert() with an empty list must not touch the database at all."""
        with patch(f"{MODULE}.MongoDatabase") as mock_client_cls:
            self.repository.insert([])
            mock_client_cls.assert_not_called()

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_insert_bulk_writes_one_operation_per_entity(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """insert() must issue one ReplaceOne per entity via bulk_write."""
        client = MagicMock()
        mock_client_cls.return_value = client
        collection = MagicMock()
        client.get_connection.return_value.__getitem__.return_value = collection

        self.repository.insert([self.entity])

        collection.bulk_write.assert_called_once()
        operations = collection.bulk_write.call_args[0][0]
        self.assertEqual(len(operations), 1)
        client.close_connection.assert_called_once()

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_bulk_write_error_wraps_into_mongo_insert_failed(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """A BulkWriteError during bulk_write must be wrapped into MongoInsertFailedError."""
        client = MagicMock()
        mock_client_cls.return_value = client
        collection = MagicMock()
        collection.bulk_write.side_effect = BulkWriteError({"writeErrors": []})
        client.get_connection.return_value.__getitem__.return_value = collection

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
