import unittest
from pathlib import Path
from scanbackup.shared import LayerConfigModel, Configuration, LayerModel


class TestConfig(unittest.TestCase):
    def test_config(self) -> None:
        config = Configuration()
        filepath = Path(config.get_filepath())
        self.assertIsNotNone(filepath)
        self.assertEqual(filepath.name, "config.yml")
        self.assertEqual(filepath.parent.name, "ScanBackup")

    def test_read_layers(self) -> None:
        config = Configuration()
        layers = config.get_cfg_layers()

        self.assertIsInstance(layers, LayerConfigModel)

        self.assertTrue(hasattr(layers, "bbip"))
        self.assertTrue(hasattr(layers, "ip"))

        self.assertIsInstance(layers.bbip, LayerModel)
        self.assertIsInstance(layers.ip, LayerModel)

        self.assertIsInstance(layers.bbip.names, list)
        self.assertIsInstance(layers.ip.names, list)


if __name__ == "__main__":
    unittest.main()
