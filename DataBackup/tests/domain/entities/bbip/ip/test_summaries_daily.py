import unittest
from datetime import date
from bson import ObjectId
from pydantic import ValidationError
from scanbackup.domain.entities.bbip.ip.summaries.daily import (
    IPDailySummaryBBIPField,
    IPDailySummaryBBIPEntity,
)


class TestIPDailySummaryBBIPField(unittest.TestCase):
    """Unit tests for the IPDailySummaryBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(IPDailySummaryBBIPField.DATE.value, "date")
        self.assertEqual(IPDailySummaryBBIPField.IN_PROM.value, "inProm")
        self.assertEqual(IPDailySummaryBBIPField.IN_MAX.value, "inMax")
        self.assertEqual(IPDailySummaryBBIPField.DEVICE.value, "id_source")


class TestIPDailySummaryBBIPEntity(unittest.TestCase):
    """Unit tests for the IPDailySummaryBBIPEntity model."""

    def test_creates_entity_with_valid_data(self) -> None:
        """A complete and well-typed payload must build a valid entity."""
        entity = IPDailySummaryBBIPEntity(
            date=date(2026, 1, 1),
            in_prom=1.0,
            in_max=2.0,
            device=ObjectId(),
        )
        self.assertEqual(entity.in_prom, 1.0)

    def test_missing_required_field_raises_validation_error(self) -> None:
        """Omitting a required field must raise a pydantic ValidationError."""
        with self.assertRaises(ValidationError):
            IPDailySummaryBBIPEntity(
                date=date(2026, 1, 1),
                in_prom=1.0,
                device=ObjectId(),
            )


if __name__ == "__main__":
    unittest.main()
