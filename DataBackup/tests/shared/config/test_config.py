from pathlib import Path
from unittest.mock import patch
from pydantic import ValidationError
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

metadata:
  dir_data: "data"
  logs:
    dir_name: "logs"
    filename: "scanbackup"
    extension: "log"
    msg_format: "%(asctime)s %(levelname)s %(message)s"
    date_format: "%Y-%m-%d %H:%M:%S"
  scanner:
    file_delimiter: ";"
    max_workers: 5
    scan_credentials:
      username: "username"
      password: "password"
  reports:
    preffix_name: "ScanBackup"
    date_format: "%Y%m%d_%H%M%S"
"""

VALID_DATABASE_ENV = {
    "SCANBACKUP_DB_HOST": "localhost",
    "SCANBACKUP_DB_PORT": "27017",
    "SCANBACKUP_DB_NAME": "scanbackup_db",
    "SCANBACKUP_DB_USER": "user",
    "SCANBACKUP_DB_PASSWORD": "password",
}


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

    def test_get_cfg_database_reads_environment_variables(self) -> None:
        """get_cfg_database must build the database model from SCANBACKUP_DB_* variables."""
        config = Configuration()
        with patch.dict("os.environ", VALID_DATABASE_ENV, clear=True):
            db_cfg = config.get_cfg_database()
        self.assertEqual(db_cfg.host, "localhost")
        self.assertEqual(db_cfg.port, 27017)
        self.assertEqual(db_cfg.name, "scanbackup_db")
        self.assertEqual(db_cfg.user, "user")
        self.assertEqual(db_cfg.password, "password")

    def test_get_cfg_database_raises_when_variable_is_missing(self) -> None:
        """get_cfg_database must fail if any SCANBACKUP_DB_* variable is not defined."""
        config = Configuration()
        incomplete_env = {
            key: value
            for key, value in VALID_DATABASE_ENV.items()
            if key != "SCANBACKUP_DB_PASSWORD"
        }
        with patch.dict("os.environ", incomplete_env, clear=True):
            with self.assertRaises(ValidationError):
                config.get_cfg_database()

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
        self.assertEqual(metadata.scanner.max_workers, 5)
        self.assertEqual(metadata.scanner.file_delimiter, ";")

    def test_get_projectpath_returns_scanbackup_parent(self) -> None:
        """get_projectpath must resolve to the repository root directory."""
        config = Configuration()
        path = Path(config.get_projectpath())
        self.assertTrue(path.is_dir())


if __name__ == "__main__":
    import unittest

    unittest.main()
