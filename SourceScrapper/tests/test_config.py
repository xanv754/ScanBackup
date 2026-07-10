import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scrapper_scanbackup.utils.config.load import ScrapperSetting
from scrapper_scanbackup.utils.config.model import ExporterModel
from scrapper_scanbackup.utils.config.paths import ENV_BASE_DIR, get_base_dir

VALID_CONFIG_YAML = """
exporter:
  dir: "data"
  delimiter: ";"
header:
  link: "link"
  interface: "interface"
  capacity: "capacity"
  type: "model"
scan_credentials:
  username: "user"
  password: "pass"
layers: []
"""


class TestGetBaseDir(unittest.TestCase):
    """Unit tests for get_base_dir, the single source of truth for config/exporter paths."""

    def test_uses_env_var_when_set(self) -> None:
        """It should return the path from SCANBACKUP_HOME when the env var is defined."""
        with patch.dict(os.environ, {ENV_BASE_DIR: "/custom/base"}):
            self.assertEqual(get_base_dir(), Path("/custom/base"))

    def test_falls_back_to_cwd_when_unset(self) -> None:
        """It should fall back to the current working directory when SCANBACKUP_HOME is unset."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ENV_BASE_DIR, None)
            self.assertEqual(get_base_dir(), Path.cwd())


class TestScrapperSettingLoadConfig(unittest.TestCase):
    """Unit tests for ScrapperSetting._load_config resolving config.yml via get_base_dir."""

    def test_loads_config_from_base_dir(self) -> None:
        """It should read config.yml from the directory returned by get_base_dir."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            (Path(tmp_dir) / "config.yml").write_text(VALID_CONFIG_YAML)
            with patch.dict(os.environ, {ENV_BASE_DIR: tmp_dir}):
                setting = ScrapperSetting()
                self.assertEqual(setting.get_scan_credentials().username, "user")

    def test_raises_when_config_missing_in_base_dir(self) -> None:
        """It should raise FileNotFoundError when config.yml is absent from the base dir."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, {ENV_BASE_DIR: tmp_dir}):
                with self.assertRaises(FileNotFoundError):
                    ScrapperSetting()


class TestExporterModelCreateDir(unittest.TestCase):
    """Unit tests for ExporterModel.create_dir resolving/creating dir via get_base_dir."""

    def test_creates_relative_dir_under_base_dir(self) -> None:
        """It should join a relative exporter dir with get_base_dir and create it."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, {ENV_BASE_DIR: tmp_dir}):
                exporter = ExporterModel(dir="data", delimiter=";")
                expected = Path(tmp_dir) / "data"
                self.assertEqual(exporter.dir, expected)
                self.assertTrue(expected.is_dir())

    def test_keeps_absolute_dir_as_is(self) -> None:
        """It should honor an absolute exporter dir instead of joining it with the base dir."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            absolute_dir = Path(tmp_dir) / "absolute-data"
            with patch.dict(os.environ, {ENV_BASE_DIR: "/should/not/be/used"}):
                exporter = ExporterModel(dir=str(absolute_dir), delimiter=";")
                self.assertEqual(exporter.dir, absolute_dir)
                self.assertTrue(absolute_dir.is_dir())


if __name__ == "__main__":
    unittest.main()
