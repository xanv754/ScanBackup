import unittest
from pydantic import ValidationError
from scanbackup.shared.config.models import (
    DatabaseConfigModel,
    LayerModel,
    LayerConfigModel,
)


class TestDatabaseConfigModel(unittest.TestCase):
    """Unit tests for the DatabaseConfigModel port range validation."""

    def _base_kwargs(self, port: int) -> dict:
        """Build valid DatabaseConfigModel kwargs with a given port."""
        return {
            "host": "localhost",
            "port": port,
            "name": "db",
            "user": "user",
            "password": "password",
        }

    def test_accepts_port_within_valid_range(self) -> None:
        """A port between 1 and 65535 must be accepted."""
        model = DatabaseConfigModel(**self._base_kwargs(27017))
        self.assertEqual(model.port, 27017)

    def test_rejects_port_below_minimum(self) -> None:
        """A port of 0 or lower must raise a ValidationError."""
        with self.assertRaises(ValidationError):
            DatabaseConfigModel(**self._base_kwargs(0))

    def test_rejects_port_above_maximum(self) -> None:
        """A port above 65535 must raise a ValidationError."""
        with self.assertRaises(ValidationError):
            DatabaseConfigModel(**self._base_kwargs(65536))


class TestLayerModel(unittest.TestCase):
    """Unit tests for the LayerModel default values."""

    def test_names_defaults_to_empty_list(self) -> None:
        """Omitting names must default to an empty list, not share state."""
        first = LayerModel(schema_collection="BBIP")
        second = LayerModel(schema_collection="IP")
        first.names.append("BORDE")
        self.assertEqual(first.names, ["BORDE"])
        self.assertEqual(second.names, [])


class TestLayerConfigModel(unittest.TestCase):
    """Unit tests for the LayerConfigModel composition."""

    def test_requires_both_bbip_and_ip_layers(self) -> None:
        """Both bbip and ip sub-models must be present to build the config."""
        model = LayerConfigModel(
            bbip=LayerModel(schema_collection="BBIP", names=["BORDE"]),
            ip=LayerModel(schema_collection="IP", names=["DINT"]),
        )
        self.assertEqual(model.bbip.names, ["BORDE"])
        self.assertEqual(model.ip.names, ["DINT"])


if __name__ == "__main__":
    unittest.main()
