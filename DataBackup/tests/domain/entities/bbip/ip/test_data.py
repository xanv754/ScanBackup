import unittest
from datetime import date, time
from bson import ObjectId
from pydantic import ValidationError
from scanbackup.domain.entities.bbip.ip.data import (
    IPActiveBBIPField,
    IPActiveBBIPEntity,
)


class TestIPActiveBBIPField(unittest.TestCase):
    """Unit tests for the IPActiveBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(IPActiveBBIPField.DATE.value, "date")
        self.assertEqual(IPActiveBBIPField.TIME.value, "time")
        self.assertEqual(IPActiveBBIPField.IN_PROM.value, "inProm")
        self.assertEqual(IPActiveBBIPField.IN_MAX.value, "inMax")
        self.assertEqual(IPActiveBBIPField.DEVICE.value, "id_source")

    def test_is_str_subclass(self) -> None:
        """Members must behave as plain strings for dict-key compatibility."""
        self.assertIsInstance(IPActiveBBIPField.DATE, str)
        self.assertEqual(IPActiveBBIPField.DATE, "date")


class TestIPActiveBBIPEntity(unittest.TestCase):
    """Unit tests for the IPActiveBBIPEntity model."""

    def test_creates_entity_with_valid_data(self) -> None:
        """A complete and well-typed payload must build a valid entity."""
        entity = IPActiveBBIPEntity(
            date=date(2026, 1, 1),
            time=time(10, 0),
            in_prom=1.5,
            in_max=2.5,
            device=ObjectId(),
        )
        self.assertEqual(entity.in_prom, 1.5)
        self.assertEqual(entity.date, date(2026, 1, 1))

    def test_missing_required_field_raises_validation_error(self) -> None:
        """Omitting a required field must raise a pydantic ValidationError."""
        with self.assertRaises(ValidationError):
            IPActiveBBIPEntity(
                date=date(2026, 1, 1),
                time=time(10, 0),
                in_prom=1.5,
                device=ObjectId(),
            )


if __name__ == "__main__":
    unittest.main()
