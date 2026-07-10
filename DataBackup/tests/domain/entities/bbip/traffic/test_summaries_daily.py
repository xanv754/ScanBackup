import unittest
from datetime import date
from bson import ObjectId
from pydantic import ValidationError
from scanbackup.domain.entities.bbip.traffic.summaries.daily import (
    TrafficDailySummaryBBIPField,
    TrafficDailySummaryBBIPEntity,
)


class TestTrafficDailySummaryBBIPField(unittest.TestCase):
    """Unit tests for the TrafficDailySummaryBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(TrafficDailySummaryBBIPField.DATE.value, "date")
        self.assertEqual(TrafficDailySummaryBBIPField.IN_PROM.value, "inProm")
        self.assertEqual(TrafficDailySummaryBBIPField.OUT_PROM.value, "outProm")
        self.assertEqual(TrafficDailySummaryBBIPField.IN_MAX.value, "inMax")
        self.assertEqual(TrafficDailySummaryBBIPField.OUT_MAX.value, "outMax")
        self.assertEqual(TrafficDailySummaryBBIPField.USE.value, "use")
        self.assertEqual(TrafficDailySummaryBBIPField.DEVICE.value, "id_source")


class TestTrafficDailySummaryBBIPEntity(unittest.TestCase):
    """Unit tests for the TrafficDailySummaryBBIPEntity model."""

    def test_creates_entity_with_valid_data(self) -> None:
        """A complete and well-typed payload must build a valid entity."""
        entity = TrafficDailySummaryBBIPEntity(
            date=date(2026, 1, 1),
            in_prom=1.0,
            in_max=2.0,
            out_prom=1.5,
            out_max=2.5,
            use=50.0,
            device=ObjectId(),
        )
        self.assertEqual(entity.use, 50.0)

    def test_missing_required_field_raises_validation_error(self) -> None:
        """Omitting a required field must raise a pydantic ValidationError."""
        with self.assertRaises(ValidationError):
            TrafficDailySummaryBBIPEntity(
                date=date(2026, 1, 1),
                in_prom=1.0,
                in_max=2.0,
                out_prom=1.5,
                device=ObjectId(),
            )


if __name__ == "__main__":
    unittest.main()
