from pathlib import Path
from scanbackup.shared.config.config import Configuration
from tests.support import TempDirTestCase

VALID_CONFIG_YAML = """
layers:
  bbip:
    schema_collection: "BBIP"
    names:
      - "BORDE"
  ip:
    schema_collection: "IP"
    names:
      - "DINT"

database:
  host: "localhost"
  port: 27017
  name: "scanbackup_db"
  user: "user"
  password: "password"

metadata:
  dir_data: "data"
  logs:
    dir_name: "logs"
    filename: "scanbackup"
    extension: "log"
    msg_format: "%(asctime)s %(levelname)s %(message)s"
    date_format: "%Y-%m-%d %H:%M:%S"
  scanner:
    dir_storage: "data"
    dir_sources: "sources"
    extension: "csv"
    date_format: "%Y-%m-%d"
    file_delimiter: ";"
    port_separator_replacement: "&"
    space_separator_replacement: "_"
    max_workers: 5
    scan_credentials:
      username: "username"
      password: "password"
  reports:
    preffix_name: "ScanBackup"
    date_format: "%Y%m%d_%H%M%S"
"""


class TestConfiguration(TempDirTestCase):
    """Unit tests for the Configuration singleton."""

    def setUp(self) -> None:
        """Point Configuration to a temporary YAML file and reset the singleton."""
        super().setUp()
        self.config_path = self.tmp_dir / "config.yml"
        self.config_path.write_text(VALID_CONFIG_YAML, encoding="utf-8")
        self._original_filepath = Configuration._filepath
        self._original_instance = Configuration._instance
        Configuration._instance = None
        Configuration._filepath = self.config_path

    def tearDown(self) -> None:
        """Restore the original Configuration singleton state."""
        Configuration._filepath = self._original_filepath
        Configuration._instance = None
        super().tearDown()

    def test_is_a_singleton(self) -> None:
        """Two instantiations must return the exact same object."""
        first = Configuration()
        second = Configuration()
        self.assertIs(first, second)

    def test_get_filepath_returns_resolved_path(self) -> None:
        """get_filepath must return the resolved path of the loaded YAML file."""
        config = Configuration()
        self.assertEqual(config.get_filepath(), str(self.config_path.resolve()))

    def test_get_cfg_database_returns_database_model(self) -> None:
        """get_cfg_database must expose the parsed database section."""
        config = Configuration()
        db_cfg = config.get_cfg_database()
        self.assertEqual(db_cfg.host, "localhost")
        self.assertEqual(db_cfg.port, 27017)

    def test_get_cfg_layers_returns_layers_model(self) -> None:
        """get_cfg_layers must expose the parsed layers section."""
        config = Configuration()
        layers = config.get_cfg_layers()
        self.assertEqual(layers.bbip.names, ["BORDE"])
        self.assertEqual(layers.ip.names, ["DINT"])

    def test_get_cfg_metadata_returns_metadata_model(self) -> None:
        """get_cfg_metadata must expose the parsed metadata section."""
        config = Configuration()
        metadata = config.get_cfg_metadata()
        self.assertEqual(metadata.dir_data, "data")
        self.assertEqual(metadata.scanner.file_delimiter, ";")

    def test_get_projectpath_returns_scanbackup_parent(self) -> None:
        """get_projectpath must resolve to the repository root directory."""
        config = Configuration()
        path = Path(config.get_projectpath())
        self.assertTrue(path.is_dir())


if __name__ == "__main__":
    import unittest

    unittest.main()
