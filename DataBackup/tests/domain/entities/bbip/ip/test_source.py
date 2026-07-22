import unittest
from unittest.mock import patch
from pydantic import ValidationError
from scanbackup.domain.entities.bbip.ip.source import (
    IPSourceBBIPField,
    IPSourceBBIPEntity,
)
from scanbackup.shared import SourceStatus


class TestIPSourceBBIPField(unittest.TestCase):
    """Unit tests for the IPSourceBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(IPSourceBBIPField.LINK.value, "link")
        self.assertEqual(IPSourceBBIPField.INTERFACE.value, "interface")
        self.assertEqual(IPSourceBBIPField.STATUS.value, "status")
        self.assertEqual(IPSourceBBIPField.LAYER.value, "layer")


class TestIPSourceBBIPEntity(unittest.TestCase):
    """Unit tests for the IPSourceBBIPEntity model."""

    @patch("scanbackup.domain.validator.ValidatorConfig.valid_layer_ip")
    def test_creates_entity_with_valid_layer(self, mock_valid_layer) -> None:
        """A layer accepted by the validator must build a valid entity."""
        mock_valid_layer.return_value = True
        entity = IPSourceBBIPEntity(
            link="http://example.com",
            interface="BRAS-00",
            layer="BRASIP",
        )
        self.assertEqual(entity.layer, "BRASIP")
        self.assertEqual(entity.status, SourceStatus.ACTIVE.value)

    @patch("scanbackup.domain.validator.ValidatorConfig.valid_layer_ip")
    def test_invalid_layer_raises_validation_error(self, mock_valid_layer) -> None:
        """A layer rejected by the validator must raise a ValidationError."""
        mock_valid_layer.return_value = False
        with self.assertRaises(ValidationError):
            IPSourceBBIPEntity(
                link="http://example.com",
                interface="BRAS-00",
                layer="UNKNOWN",
            )

    @patch("scanbackup.domain.validator.ValidatorConfig.valid_layer_ip")
    def test_id_is_optional(self, mock_valid_layer) -> None:
        """id must remain optional and default to None."""
        mock_valid_layer.return_value = True
        entity = IPSourceBBIPEntity(
            link="http://example.com",
            interface="BRAS-00",
            layer="BRASIP",
        )
        self.assertIsNone(entity.id)


if __name__ == "__main__":
    unittest.main()
