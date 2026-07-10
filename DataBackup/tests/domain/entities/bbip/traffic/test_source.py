import unittest
from unittest.mock import patch
from pydantic import ValidationError
from scanbackup.domain.entities.bbip.traffic.source import (
    TrafficSourceBBIPField,
    TrafficSourceBBIPEntity,
)
from scanbackup.shared import SourceStatus


class TestTrafficSourceBBIPField(unittest.TestCase):
    """Unit tests for the TrafficSourceBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(TrafficSourceBBIPField.LINK.value, "link")
        self.assertEqual(TrafficSourceBBIPField.INTERFACE.value, "interface")
        self.assertEqual(TrafficSourceBBIPField.CAPACITY.value, "capacity")
        self.assertEqual(TrafficSourceBBIPField.MODEL.value, "model")
        self.assertEqual(TrafficSourceBBIPField.STATUS.value, "status")
        self.assertEqual(TrafficSourceBBIPField.LAYER.value, "layer")
        self.assertEqual(TrafficSourceBBIPField.COMMENTS.value, "comments")


class TestTrafficSourceBBIPEntity(unittest.TestCase):
    """Unit tests for the TrafficSourceBBIPEntity model."""

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_bbip")
    def test_creates_entity_with_valid_layer(self, mock_valid_layer) -> None:
        """A layer accepted by the validator must build a valid entity."""
        mock_valid_layer.return_value = True
        entity = TrafficSourceBBIPEntity(
            link="http://example.com",
            interface="Gi0/0/0",
            capacity=100.0,
            model="Cisco",
            layer="BORDE",
        )
        self.assertEqual(entity.layer, "BORDE")
        self.assertEqual(entity.status, SourceStatus.ACTIVE.value)

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_bbip")
    def test_invalid_layer_raises_validation_error(self, mock_valid_layer) -> None:
        """A layer rejected by the validator must raise a ValidationError."""
        mock_valid_layer.return_value = False
        with self.assertRaises(ValidationError):
            TrafficSourceBBIPEntity(
                link="http://example.com",
                interface="Gi0/0/0",
                capacity=100.0,
                model="Cisco",
                layer="UNKNOWN",
            )

    @patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_bbip")
    def test_default_status_and_optional_fields(self, mock_valid_layer) -> None:
        """device and comments must remain optional and default to None."""
        mock_valid_layer.return_value = True
        entity = TrafficSourceBBIPEntity(
            link="http://example.com",
            interface="Gi0/0/0",
            capacity=100.0,
            model="Cisco",
            layer="BORDE",
        )
        self.assertIsNone(entity.device)
        self.assertIsNone(entity.comments)


if __name__ == "__main__":
    unittest.main()
