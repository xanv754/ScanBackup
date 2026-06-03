import unittest
from unittest.mock import patch
from scrapper_scanbackup.utils.config.load import ScrapperSetting

VALID_YAML = """
exporter:
  dir: exports/
  delimiter: ","

scan_credentials:
  username: admin
  password: secret123

layers:
  - layer: layer_a
    url: http://host-a/api
    type: REST
    locked: false
    credentials:
      username: user_a
      password: pass_a
  - layer: layer_b
    url: http://host-b/api
    type: REST
    locked: true
  - layer: layer_a
    url: http://host-a2/api
    type: REST
    locked: false
"""


def _make_setting(yaml_content: str = VALID_YAML) -> ScrapperSetting:
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.read_text", return_value=yaml_content),
        patch("pathlib.Path.mkdir"),
    ):
        return ScrapperSetting()


class TestScrapperSettingInit(unittest.TestCase):
    def test_loads_config_on_init(self):
        setting = _make_setting()
        self.assertIsNotNone(setting._config)

    def test_raises_when_config_file_missing(self):
        with patch("pathlib.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                ScrapperSetting()

    def test_raises_on_invalid_yaml_structure(self):
        with self.assertRaises(Exception):
            _make_setting("not_a_valid_key: value")


class TestGetExporter(unittest.TestCase):
    def setUp(self):
        self.setting = _make_setting()

    def test_returns_exporter_model(self):
        from scrapper_scanbackup.utils.config.model import ExporterModel

        self.assertIsInstance(self.setting.get_exporter(), ExporterModel)

    def test_returns_correct_delimiter(self):
        self.assertEqual(self.setting.get_exporter().delimiter, ",")

    def test_dir_is_resolved_path(self):
        from pathlib import Path

        self.assertIsInstance(self.setting.get_exporter().dir, Path)


class TestGetScanCredentials(unittest.TestCase):
    def setUp(self):
        self.setting = _make_setting()

    def test_returns_correct_username(self):
        self.assertEqual(self.setting.get_scan_credentials().username, "admin")

    def test_returns_correct_password(self):
        self.assertEqual(self.setting.get_scan_credentials().password, "secret123")


class TestGetDataLayer(unittest.TestCase):
    def setUp(self):
        self.setting = _make_setting()

    def test_returns_matching_layers(self):
        self.assertEqual(len(self.setting.get_data_layer("layer_a")), 2)

    def test_returns_correct_urls_for_layer(self):
        urls = {l.url for l in self.setting.get_data_layer("layer_a")}
        self.assertEqual(urls, {"http://host-a/api", "http://host-a2/api"})

    def test_returns_empty_list_when_no_match(self):
        self.assertEqual(self.setting.get_data_layer("nonexistent_layer"), [])

    def test_layer_with_credentials(self):
        layer = next(
            l
            for l in self.setting.get_data_layer("layer_a")
            if l.url == "http://host-a/api"
        )
        self.assertIsNotNone(layer.credentials)
        self.assertEqual(layer.credentials.username, "user_a")

    def test_layer_without_credentials_is_none(self):
        self.assertIsNone(self.setting.get_data_layer("layer_b")[0].credentials)

    def test_locked_flag_is_parsed_correctly(self):
        self.assertTrue(self.setting.get_data_layer("layer_b")[0].locked)
        self.assertFalse(self.setting.get_data_layer("layer_a")[0].locked)


if __name__ == "__main__":
    unittest.main()
