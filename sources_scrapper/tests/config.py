import unittest
from unittest.mock import patch
from scrapper_scanbackup.utils.config.load import ScrapperSetting

VALID_YAML = """
scan_credentials:
  user: admin
  password: secret123

layers:
  - layer: layer_a
    url: http://host-a/api
    type: REST
    locked: false
    credentials:
      user: user_a
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
    """Instancia ScrapperSetting mockeando el archivo de configuración."""
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.read_text", return_value=yaml_content),
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
        invalid_yaml = "not_a_valid_key: value"
        with self.assertRaises(Exception):
            _make_setting(invalid_yaml)


class TestGetScanCredentials(unittest.TestCase):
    def setUp(self):
        self.setting = _make_setting()

    def test_returns_correct_user(self):
        cred = self.setting.get_scan_credentials()
        self.assertEqual(cred.username, "admin")

    def test_returns_correct_password(self):
        cred = self.setting.get_scan_credentials()
        self.assertEqual(cred.password, "secret123")


class TestGetDataLayer(unittest.TestCase):
    def setUp(self):
        self.setting = _make_setting()

    def test_returns_matching_layers(self):
        result = self.setting.get_data_layer("layer_a")
        self.assertEqual(len(result), 2)

    def test_returns_correct_urls_for_layer(self):
        result = self.setting.get_data_layer("layer_a")
        urls = {layer.url for layer in result}
        self.assertEqual(urls, {"http://host-a/api", "http://host-a2/api"})

    def test_returns_empty_list_when_no_match(self):
        result = self.setting.get_data_layer("nonexistent_layer")
        self.assertEqual(result, [])

    def test_layer_with_credentials(self):
        result = self.setting.get_data_layer("layer_a")
        layer = next(l for l in result if l.url == "http://host-a/api")
        self.assertIsNotNone(layer.credentials)
        self.assertEqual(layer.credentials.username, "user_a")

    def test_layer_without_credentials_is_none(self):
        result = self.setting.get_data_layer("layer_b")
        self.assertIsNone(result[0].credentials)

    def test_locked_flag_is_parsed_correctly(self):
        locked_layer = self.setting.get_data_layer("layer_b")[0]
        self.assertTrue(locked_layer.locked)

        unlocked_layer = self.setting.get_data_layer("layer_a")[0]
        self.assertFalse(unlocked_layer.locked)


if __name__ == "__main__":
    unittest.main()
