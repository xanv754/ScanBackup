import unittest
from unittest.mock import MagicMock, patch
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.shared import (
    DatabaseConfigModel,
    LayerConfigModel,
    LayerModel,
    MongoConnectionError,
    MongoCollectionNotFoundError,
    FileImportNotFoundError,
    FileExtensionError,
    LayerNotDefined,
)

MODULE = "scanbackup.infrastructure.persistence.mongodb.connections.database"


class TestMongoDatabase(unittest.TestCase):
    """Unit tests for the MongoDatabase connection manager."""

    def setUp(self) -> None:
        """Reset the MongoDatabase singleton before each test."""
        MongoDatabase._instance = None
        self.db_config = DatabaseConfigModel(
            host="localhost", port=27017, name="scanbackup_db", user="user", password="pass"
        )
        self.layers_config = LayerConfigModel(
            bbip=LayerModel(schema_collection="BBIP", names=["BORDE"]),
            ip=LayerModel(schema_collection="IP", names=["DINT"]),
        )

    def tearDown(self) -> None:
        """Reset the MongoDatabase singleton after each test."""
        MongoDatabase._instance = None

    def test_is_a_singleton(self) -> None:
        """Two instantiations must return the exact same object."""
        self.assertIs(MongoDatabase(), MongoDatabase())

    def test_set_uri_and_get_uri(self) -> None:
        """set_uri must build a well-formed mongodb:// URI from the config."""
        db = MongoDatabase()
        db.set_uri(self.db_config)
        self.assertEqual(
            db.get_uri(),
            "mongodb://user:pass@localhost:27017/scanbackup_db?authSource=scanbackup_db",
        )

    @patch(f"{MODULE}.MongoClient")
    def test_open_connection_marks_as_connected(self, mock_client_cls) -> None:
        """open_connection must instantiate a MongoClient and flag connected=True."""
        db = MongoDatabase()
        db.set_uri(self.db_config)

        db.open_connection()

        mock_client_cls.assert_called_once_with(db.get_uri())
        self.assertTrue(db.connected)

    @patch(f"{MODULE}.MongoClient")
    def test_open_connection_failure_raises_mongo_connection_error(self, mock_client_cls) -> None:
        """A MongoClient failure must be wrapped into MongoConnectionError."""
        mock_client_cls.side_effect = RuntimeError("unreachable")
        db = MongoDatabase()
        db.set_uri(self.db_config)

        with self.assertRaises(MongoConnectionError):
            db.open_connection()
        self.assertFalse(db.connected)

    @patch(f"{MODULE}.MongoClient")
    def test_close_connection_marks_as_disconnected(self, mock_client_cls) -> None:
        """close_connection must close the client and flag connected=False."""
        db = MongoDatabase()
        db.set_uri(self.db_config)
        db.open_connection()

        db.close_connection()

        self.assertFalse(db.connected)

    @patch(f"{MODULE}.TrafficSourceBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_create_collections_skips_existing_collections(
        self, mock_client_cls, mock_traffic_source_collection
    ) -> None:
        """create_collections must not recreate a collection that already exists."""
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["TRAFFIC_SOURCE_BBIP"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db

        db = MongoDatabase()
        db.set_uri(self.db_config)
        db.create_collections(
            LayerConfigModel(
                bbip=LayerModel(schema_collection="BBIP", names=[]),
                ip=LayerModel(schema_collection="IP", names=[]),
            )
        )

        mock_traffic_source_collection.create.assert_not_called()

    @patch(f"{MODULE}.IPHistoryBBIPCollection")
    @patch(f"{MODULE}.TrafficHistoryBBIPCollection")
    @patch(f"{MODULE}.IPDailySummaryBBIPCollection")
    @patch(f"{MODULE}.IPSourceBBIPCollection")
    @patch(f"{MODULE}.TrafficDailySummaryBBIPCollection")
    @patch(f"{MODULE}.TrafficSourceBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_create_collections_creates_missing_collections(
        self,
        mock_client_cls,
        mock_traffic_source,
        mock_traffic_daily,
        mock_ip_source,
        mock_ip_daily,
        mock_traffic_history,
        mock_ip_history,
    ) -> None:
        """create_collections must create every collection absent from the database."""
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = []
        mock_client_cls.return_value.__getitem__.return_value = mock_db

        db = MongoDatabase()
        db.set_uri(self.db_config)
        db.create_collections(self.layers_config)

        mock_traffic_source.create.assert_called_once()
        mock_traffic_daily.create.assert_called_once()
        mock_ip_source.create.assert_called_once()
        mock_ip_daily.create.assert_called_once()
        mock_traffic_history.create.assert_called_once()
        mock_ip_history.create.assert_called_once()

    @patch(f"{MODULE}.MongoClient")
    def test_import_data_missing_file_raises(self, mock_client_cls) -> None:
        """import_data must raise FileImportNotFoundError for a missing input file."""
        db = MongoDatabase()
        db.set_uri(self.db_config)

        with self.assertRaises(FileImportNotFoundError):
            db.import_data(
                name_collection="BORDE",
                config=self.layers_config,
                input_filepath="/tmp/does-not-exist.csv",
                delimiter=";",
            )

    @patch(f"{MODULE}.MongoClient")
    def test_import_data_wrong_extension_raises(self, mock_client_cls) -> None:
        """import_data must raise FileExtensionError for a non csv/txt input file."""
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".xls") as tmp_file:
            db = MongoDatabase()
            db.set_uri(self.db_config)

            with self.assertRaises(FileExtensionError):
                db.import_data(
                    name_collection="BORDE",
                    config=self.layers_config,
                    input_filepath=tmp_file.name,
                    delimiter=";",
                )

    @patch(f"{MODULE}.MongoClient")
    def test_import_data_unknown_collection_raises(self, mock_client_cls) -> None:
        """import_data must raise MongoCollectionNotFoundError if the collection is absent."""
        import tempfile

        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = []
        mock_client_cls.return_value.__getitem__.return_value = mock_db

        with tempfile.NamedTemporaryFile(suffix=".csv") as tmp_file:
            db = MongoDatabase()
            db.set_uri(self.db_config)

            with self.assertRaises(MongoCollectionNotFoundError):
                db.import_data(
                    name_collection="BORDE",
                    config=self.layers_config,
                    input_filepath=tmp_file.name,
                    delimiter=";",
                )

    @patch(f"{MODULE}.TrafficHistoryBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_import_data_routes_bbip_layer_to_traffic_history(
        self, mock_client_cls, mock_traffic_history
    ) -> None:
        """A collection name matching a BBIP layer must route to TrafficHistoryBBIPCollection."""
        import tempfile

        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["BORDE"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db

        with tempfile.NamedTemporaryFile(suffix=".csv") as tmp_file:
            db = MongoDatabase()
            db.set_uri(self.db_config)
            db.import_data(
                name_collection="BORDE",
                config=self.layers_config,
                input_filepath=tmp_file.name,
                delimiter=";",
            )

        mock_traffic_history.import_data.assert_called_once()

    @patch(f"{MODULE}.MongoClient")
    def test_import_data_undefined_layer_raises(self, mock_client_cls) -> None:
        """A collection name matching no known layer or fixed name must raise LayerNotDefined."""
        import tempfile

        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["UNKNOWN"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db

        with tempfile.NamedTemporaryFile(suffix=".csv") as tmp_file:
            db = MongoDatabase()
            db.set_uri(self.db_config)

            with self.assertRaises(LayerNotDefined):
                db.import_data(
                    name_collection="UNKNOWN",
                    config=self.layers_config,
                    input_filepath=tmp_file.name,
                    delimiter=";",
                )

    @patch(f"{MODULE}.MongoClient")
    def test_export_data_unknown_collection_raises(self, mock_client_cls) -> None:
        """export_data must raise MongoCollectionNotFoundError if the collection is absent."""
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = []
        mock_client_cls.return_value.__getitem__.return_value = mock_db

        db = MongoDatabase()
        db.set_uri(self.db_config)

        with self.assertRaises(MongoCollectionNotFoundError):
            db.export_data(config=self.layers_config, name_collection="BORDE")

    @patch(f"{MODULE}.TrafficSourceBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_export_data_returns_the_collection_filepath(
        self, mock_client_cls, mock_traffic_source
    ) -> None:
        """export_data must return the filepath produced by the routed collection class."""
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["TRAFFIC_SOURCE_BBIP"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db
        mock_traffic_source.export_data.return_value = "/tmp/traffic_source.csv"

        db = MongoDatabase()
        db.set_uri(self.db_config)
        result = db.export_data(
            config=self.layers_config, name_collection="TRAFFIC_SOURCE_BBIP"
        )

        self.assertEqual(result, "/tmp/traffic_source.csv")


if __name__ == "__main__":
    unittest.main()
