import unittest
from unittest.mock import MagicMock, patch
from bson import ObjectId
from pymongo.errors import BulkWriteError
from scanbackup.infrastructure.persistence.mongodb.repositories.bbip.ip.source import (
    MongoIPSourceBBIPRepository,
)
from scanbackup.domain import IPSourceBBIPEntity
from scanbackup.shared import (
    MongoInsertFailedError,
    MongoGetFailedError,
    MongoConnectionError,
)

MODULE = "scanbackup.infrastructure.persistence.mongodb.repositories.bbip.ip.source"


class TestMongoIPSourceBBIPRepository(unittest.TestCase):
    """Unit tests for the MongoIPSourceBBIPRepository."""

    def setUp(self) -> None:
        """Build a repository instance for reuse across tests."""
        self.repository = MongoIPSourceBBIPRepository()

    def _mock_client(self, mock_client_cls) -> MagicMock:
        """Return the client returned by the patched MongoDatabase class."""
        client = MagicMock()
        mock_client_cls.return_value = client
        return client

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_get_existing_keys_projects_expected_fields(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """get_existing_keys must project only interface/layer, excluding _id."""
        client = self._mock_client(mock_client_cls)
        collection = MagicMock()
        collection.find.return_value = [
            {"interface": "BRAS-00", "layer": "BRASIP"}
        ]
        client.get_connection.return_value.__getitem__.return_value = collection

        result = self.repository.get_existing_keys()

        self.assertEqual(result, [{"interface": "BRAS-00", "layer": "BRASIP"}])
        client.close_connection.assert_called_once()

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_get_existing_keys_wraps_generic_error(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """Any unexpected failure must be wrapped into MongoGetFailedError."""
        client = self._mock_client(mock_client_cls)
        client.get_connection.side_effect = RuntimeError("boom")

        with self.assertRaises(MongoGetFailedError):
            self.repository.get_existing_keys()

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_get_existing_keys_propagates_connection_error(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """A MongoConnectionError must propagate unchanged."""
        client = self._mock_client(mock_client_cls)
        client.open_connection.side_effect = MongoConnectionError()

        with self.assertRaises(MongoConnectionError):
            self.repository.get_existing_keys()

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_upsert_sources_bulk_writes_one_operation_per_entity(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """upsert_sources must issue one UpdateOne per entity."""
        client = self._mock_client(mock_client_cls)
        collection = MagicMock()
        client.get_connection.return_value.__getitem__.return_value = collection

        with patch(
            "scanbackup.domain.services.validator.ValidatorConfig.valid_layer_ip",
            return_value=True,
        ):
            entity = IPSourceBBIPEntity(
                link="http://example.com",
                interface="BRAS-00",
                layer="BRASIP",
            )
            self.repository.upsert_sources([entity])

        collection.bulk_write.assert_called_once()
        operations = collection.bulk_write.call_args[0][0]
        self.assertEqual(len(operations), 1)

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_upsert_sources_bulk_write_error_wraps(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """A BulkWriteError during upsert must be wrapped into MongoInsertFailedError."""
        client = self._mock_client(mock_client_cls)
        collection = MagicMock()
        collection.bulk_write.side_effect = BulkWriteError({"writeErrors": []})
        client.get_connection.return_value.__getitem__.return_value = collection

        with self.assertRaises(MongoInsertFailedError):
            self.repository.upsert_sources([])

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_discontinue_missing_updates_documents_not_in_present_keys(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """discontinue_missing must update every document outside the present keys."""
        client = self._mock_client(mock_client_cls)
        collection = MagicMock()
        client.get_connection.return_value.__getitem__.return_value = collection

        self.repository.discontinue_missing(
            [{"interface": "BRAS-00", "layer": "BRASIP"}]
        )

        collection.update_many.assert_called_once()

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_get_sources_by_layer_maps_documents_to_entities(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """get_sources_by_layer must map found documents into domain entities."""
        client = self._mock_client(mock_client_cls)
        collection = MagicMock()
        collection.find.return_value = [
            {
                "link": "http://example.com",
                "interface": "BRAS-00",
                "layer": "BRASIP",
                "status": "ACTIVO",
            }
        ]
        client.get_connection.return_value.__getitem__.return_value = collection

        with patch(
            "scanbackup.domain.services.validator.ValidatorConfig.valid_layer_ip",
            return_value=True,
        ):
            result = self.repository.get_sources_by_layer("BRASIP")

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], IPSourceBBIPEntity)

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_get_sources_by_layer_id_uses_mongo_id_as_id(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """get_sources_by_layer_id must map the Mongo '_id' into the entity's id field."""
        client = self._mock_client(mock_client_cls)
        collection = MagicMock()
        oid = ObjectId()
        collection.find.return_value = [
            {
                "_id": oid,
                "link": "http://example.com",
                "interface": "BRAS-00",
                "layer": "BRASIP",
                "status": "ACTIVO",
            }
        ]
        client.get_connection.return_value.__getitem__.return_value = collection

        with patch(
            "scanbackup.domain.services.validator.ValidatorConfig.valid_layer_ip",
            return_value=True,
        ):
            result = self.repository.get_sources_by_layer_id("BRASIP")

        self.assertEqual(result[0].id, oid)
        self.assertEqual(result[0].interface, "BRAS-00")

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_get_all_active_sources_queries_without_a_layer_filter(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """get_all_active_sources must filter only by status, across every layer."""
        client = self._mock_client(mock_client_cls)
        collection = MagicMock()
        oid = ObjectId()
        collection.find.return_value = [
            {
                "_id": oid,
                "link": "http://example.com",
                "interface": "BRAS-00",
                "layer": "BRASIP",
                "status": "ACTIVO",
            }
        ]
        client.get_connection.return_value.__getitem__.return_value = collection

        with patch(
            "scanbackup.domain.services.validator.ValidatorConfig.valid_layer_ip",
            return_value=True,
        ):
            result = self.repository.get_all_active_sources()

        collection.find.assert_called_once_with({"status": "ACTIVO"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, oid)

    @patch(f"{MODULE}.Configuration")
    @patch(f"{MODULE}.MongoDatabase")
    def test_get_all_sources_queries_without_any_filter(
        self, mock_client_cls, mock_configuration
    ) -> None:
        """get_all_sources must query the whole collection, including discontinued sources."""
        client = self._mock_client(mock_client_cls)
        collection = MagicMock()
        oid = ObjectId()
        collection.find.return_value = [
            {
                "_id": oid,
                "link": "http://example.com",
                "interface": "BRAS-00",
                "layer": "BRASIP",
                "status": "DESINCORPORADO",
            }
        ]
        client.get_connection.return_value.__getitem__.return_value = collection

        with patch(
            "scanbackup.domain.services.validator.ValidatorConfig.valid_layer_ip",
            return_value=True,
        ):
            result = self.repository.get_all_sources()

        collection.find.assert_called_once_with({})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, oid)


if __name__ == "__main__":
    unittest.main()
