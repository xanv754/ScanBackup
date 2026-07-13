import unittest
from datetime import date, time
from bson import ObjectId
from pydantic import ValidationError
from scanbackup.domain.entities.bbip.ip.summaries.hour import (
    IPHourSummaryBBIPField,
    IPHourSummaryBBIPEntity,
)


class TestIPHourSummaryBBIPField(unittest.TestCase):
    """Unit tests for the IPHourSummaryBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(IPHourSummaryBBIPField.DATE.value, "date")
        self.assertEqual(IPHourSummaryBBIPField.TIME.value, "time")
        self.assertEqual(IPHourSummaryBBIPField.IN_PROM.value, "inProm")
        self.assertEqual(IPHourSummaryBBIPField.IN_MAX.value, "inMax")
        self.assertEqual(IPHourSummaryBBIPField.DEVICE.value, "id_source")


class TestIPHourSummaryBBIPEntity(unittest.TestCase):
    """Unit tests for the IPHourSummaryBBIPEntity model."""

    def test_creates_entity_with_valid_data(self) -> None:
        """A complete and well-typed payload must build a valid entity."""
        entity = IPHourSummaryBBIPEntity(
            date=date(2026, 1, 1),
            time=time(13, 0, 0),
            in_prom=1.0,
            in_max=2.0,
            device=ObjectId(),
        )
        self.assertEqual(entity.time, time(13, 0, 0))
        self.assertEqual(entity.in_prom, 1.0)

    def test_missing_required_field_raises_validation_error(self) -> None:
        """Omitting a required field must raise a pydantic ValidationError."""
        with self.assertRaises(ValidationError):
            IPHourSummaryBBIPEntity(
                date=date(2026, 1, 1),
                in_prom=1.0,
                device=ObjectId(),
            )


if __name__ == "__main__":
    unittest.main()
