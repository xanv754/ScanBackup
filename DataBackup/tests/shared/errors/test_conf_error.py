import unittest
from unittest.mock import patch
from scanbackup.shared.errors.conf_error import (
    ConfigError,
    SchemaConfigError,
    ValueConfigError,
    LayerNotDefined,
)
from scanbackup.shared.errors.system import ScanBackupError


@patch("scanbackup.shared.errors.system.Terminal")
@patch("scanbackup.shared.errors.system.Log")
class TestConfError(unittest.TestCase):
    """Unit tests for the configuration error hierarchy."""

    def test_config_error_default_message(self, mock_log, mock_terminal) -> None:
        """ConfigError without a message must use the default text."""
        error = ConfigError()
        self.assertIn("configuración", str(error))
        self.assertIsInstance(error, ScanBackupError)

    def test_schema_config_error_appends_extra_msg(self, mock_log, mock_terminal) -> None:
        """SchemaConfigError must append the extra message when provided."""
        error = SchemaConfigError(extra_msg="campo faltante")
        self.assertIn("campo faltante", str(error))

    def test_value_config_error_appends_extra_msg(self, mock_log, mock_terminal) -> None:
        """ValueConfigError must append the extra message when provided."""
        error = ValueConfigError(extra_msg="valor fuera de rango")
        self.assertIn("valor fuera de rango", str(error))

    def test_layer_not_defined_includes_layer_name(self, mock_log, mock_terminal) -> None:
        """LayerNotDefined must include the offending layer name in the message."""
        error = LayerNotDefined("DESCONOCIDA")
        self.assertIn("DESCONOCIDA", str(error))


if __name__ == "__main__":
    unittest.main()
