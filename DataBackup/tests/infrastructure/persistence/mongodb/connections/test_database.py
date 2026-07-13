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

    @patch(f"{MODULE}.IPHourSummaryBBIPCollection")
    @patch(f"{MODULE}.TrafficHourSummaryBBIPCollection")
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
        mock_traffic_hour,
        mock_ip_hour,
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
        mock_traffic_hour.create.assert_called_once()
        mock_ip_hour.create.assert_called_once()

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
        """A collection name matching a BBIP layer's history collection must route to TrafficHistoryBBIPCollection."""
        import tempfile

        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["BORDE_TRAFFIC_HISTORY_BBIP"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db

        with tempfile.NamedTemporaryFile(suffix=".csv") as tmp_file:
            db = MongoDatabase()
            db.set_uri(self.db_config)
            db.import_data(
                name_collection="BORDE_TRAFFIC_HISTORY_BBIP",
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

    @patch(f"{MODULE}.TrafficSourceBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_export_data_propagates_dirpath_to_the_collection(
        self, mock_client_cls, mock_traffic_source
    ) -> None:
        """export_data must forward the given dirpath to the routed collection class."""
        from pathlib import Path

        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["TRAFFIC_SOURCE_BBIP"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db

        db = MongoDatabase()
        db.set_uri(self.db_config)
        db.export_data(
            config=self.layers_config,
            name_collection="TRAFFIC_SOURCE_BBIP",
            dirpath=Path("/tmp/exports"),
        )

        mock_traffic_source.export_data.assert_called_once_with(
            database=mock_db, dirpath=Path("/tmp/exports"), include_id=True
        )

    @patch(f"{MODULE}.TrafficHistoryBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_export_data_routes_bbip_layer_to_traffic_history(
        self, mock_client_cls, mock_traffic_history
    ) -> None:
        """A collection name matching a BBIP layer's history collection must route to TrafficHistoryBBIPCollection."""
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["BORDE_TRAFFIC_HISTORY_BBIP"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db
        mock_traffic_history.export_data.return_value = "/tmp/borde.csv"

        db = MongoDatabase()
        db.set_uri(self.db_config)
        result = db.export_data(
            config=self.layers_config, name_collection="BORDE_TRAFFIC_HISTORY_BBIP"
        )

        mock_traffic_history.export_data.assert_called_once()
        self.assertEqual(result, "/tmp/borde.csv")

    @patch(f"{MODULE}.IPHistoryBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_export_data_routes_ip_layer_to_ip_history(
        self, mock_client_cls, mock_ip_history
    ) -> None:
        """A collection name matching an IP layer's history collection must route to IPHistoryBBIPCollection."""
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["DINT_IP_HISTORY_BBIP"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db
        mock_ip_history.export_data.return_value = "/tmp/dint.csv"

        db = MongoDatabase()
        db.set_uri(self.db_config)
        result = db.export_data(
            config=self.layers_config, name_collection="DINT_IP_HISTORY_BBIP"
        )

        mock_ip_history.export_data.assert_called_once()
        self.assertEqual(result, "/tmp/dint.csv")

    def test_match_history_layer_requires_the_exact_suffix(self) -> None:
        """A collection name without the history suffix must never match, even with a valid layer prefix."""
        db = MongoDatabase()

        self.assertFalse(
            db._match_history_layer("BORDE", ["BORDE"], "TRAFFIC_HISTORY_BBIP")
        )
        self.assertFalse(
            db._match_history_layer(
                "BORDE_SOMETHING_ELSE", ["BORDE"], "TRAFFIC_HISTORY_BBIP"
            )
        )

    def test_match_history_layer_is_case_insensitive(self) -> None:
        """Layer name comparison must ignore case in both the collection and the config."""
        db = MongoDatabase()

        self.assertTrue(
            db._match_history_layer(
                "borde_traffic_history_bbip", ["BORDE"], "TRAFFIC_HISTORY_BBIP"
            )
        )

    def test_match_history_layer_rejects_unconfigured_layers(self) -> None:
        """A well-formed history collection name for an unconfigured layer must not match."""
        db = MongoDatabase()

        self.assertFalse(
            db._match_history_layer(
                "UNKNOWN_TRAFFIC_HISTORY_BBIP", ["BORDE"], "TRAFFIC_HISTORY_BBIP"
            )
        )

    @patch(f"{MODULE}.TrafficHourSummaryBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_import_data_routes_traffic_hour_summary(
        self, mock_client_cls, mock_traffic_hour
    ) -> None:
        """The traffic hour summary collection name must route to TrafficHourSummaryBBIPCollection."""
        import tempfile

        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["TRAFFIC_HOUR_SUMMARY_BBIP"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db

        with tempfile.NamedTemporaryFile(suffix=".csv") as tmp_file:
            db = MongoDatabase()
            db.set_uri(self.db_config)
            db.import_data(
                name_collection="TRAFFIC_HOUR_SUMMARY_BBIP",
                config=self.layers_config,
                input_filepath=tmp_file.name,
                delimiter=";",
            )

        mock_traffic_hour.import_data.assert_called_once()

    @patch(f"{MODULE}.IPHourSummaryBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_import_data_routes_ip_hour_summary(
        self, mock_client_cls, mock_ip_hour
    ) -> None:
        """The IP hour summary collection name must route to IPHourSummaryBBIPCollection."""
        import tempfile

        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["IP_HOUR_SUMMARY_BBIP"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db

        with tempfile.NamedTemporaryFile(suffix=".csv") as tmp_file:
            db = MongoDatabase()
            db.set_uri(self.db_config)
            db.import_data(
                name_collection="IP_HOUR_SUMMARY_BBIP",
                config=self.layers_config,
                input_filepath=tmp_file.name,
                delimiter=";",
            )

        mock_ip_hour.import_data.assert_called_once()

    @patch(f"{MODULE}.TrafficHourSummaryBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_export_data_routes_traffic_hour_summary(
        self, mock_client_cls, mock_traffic_hour
    ) -> None:
        """The traffic hour summary collection name must route to TrafficHourSummaryBBIPCollection."""
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["TRAFFIC_HOUR_SUMMARY_BBIP"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db
        mock_traffic_hour.export_data.return_value = "/tmp/traffic_hour.csv"

        db = MongoDatabase()
        db.set_uri(self.db_config)
        result = db.export_data(
            config=self.layers_config, name_collection="TRAFFIC_HOUR_SUMMARY_BBIP"
        )

        self.assertEqual(result, "/tmp/traffic_hour.csv")

    @patch(f"{MODULE}.IPHourSummaryBBIPCollection")
    @patch(f"{MODULE}.MongoClient")
    def test_export_data_routes_ip_hour_summary(
        self, mock_client_cls, mock_ip_hour
    ) -> None:
        """The IP hour summary collection name must route to IPHourSummaryBBIPCollection."""
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["IP_HOUR_SUMMARY_BBIP"]
        mock_client_cls.return_value.__getitem__.return_value = mock_db
        mock_ip_hour.export_data.return_value = "/tmp/ip_hour.csv"

        db = MongoDatabase()
        db.set_uri(self.db_config)
        result = db.export_data(
            config=self.layers_config, name_collection="IP_HOUR_SUMMARY_BBIP"
        )

        self.assertEqual(result, "/tmp/ip_hour.csv")


if __name__ == "__main__":
    unittest.main()
