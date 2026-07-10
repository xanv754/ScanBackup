import unittest
from unittest.mock import MagicMock, patch
from scanbackup.domain.services.validator import ValidatorConfig


class TestValidatorConfig(unittest.TestCase):
    """Unit tests for the ValidatorConfig service."""

    def _mock_configuration(self, bbip_names: list[str], ip_names: list[str]) -> MagicMock:
        """Build a fake Configuration returning the given layer names."""
        cfg_layers = MagicMock()
        cfg_layers.bbip.names = bbip_names
        cfg_layers.ip.names = ip_names
        config = MagicMock()
        config.get_cfg_layers.return_value = cfg_layers
        return config

    @patch("scanbackup.domain.services.validator.Configuration")
    def test_valid_layer_bbip_matches_case_insensitively(self, mock_configuration) -> None:
        """A BBIP layer name must match regardless of input case."""
        mock_configuration.return_value = self._mock_configuration(["borde"], [])
        self.assertTrue(ValidatorConfig.valid_layer_bbip("BORDE"))

    @patch("scanbackup.domain.services.validator.Configuration")
    def test_valid_layer_bbip_rejects_unknown_layer(self, mock_configuration) -> None:
        """A layer absent from the BBIP configuration must be rejected."""
        mock_configuration.return_value = self._mock_configuration(["borde"], [])
        self.assertFalse(ValidatorConfig.valid_layer_bbip("UNKNOWN"))

    @patch("scanbackup.domain.services.validator.Configuration")
    def test_valid_layer_ip_matches_case_insensitively(self, mock_configuration) -> None:
        """An IP layer name must match regardless of input case."""
        mock_configuration.return_value = self._mock_configuration([], ["dint"])
        self.assertTrue(ValidatorConfig.valid_layer_ip("DINT"))

    @patch("scanbackup.domain.services.validator.Configuration")
    def test_valid_layer_ip_rejects_unknown_layer(self, mock_configuration) -> None:
        """A layer absent from the IP configuration must be rejected."""
        mock_configuration.return_value = self._mock_configuration([], ["dint"])
        self.assertFalse(ValidatorConfig.valid_layer_ip("UNKNOWN"))


if __name__ == "__main__":
    unittest.main()
