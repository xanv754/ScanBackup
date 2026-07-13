import unittest
from datetime import date, time
from bson import ObjectId
from pydantic import ValidationError
from scanbackup.domain.entities.bbip.traffic.summaries.hour import (
    TrafficHourSummaryBBIPField,
    TrafficHourSummaryBBIPEntity,
)


class TestTrafficHourSummaryBBIPField(unittest.TestCase):
    """Unit tests for the TrafficHourSummaryBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(TrafficHourSummaryBBIPField.DATE.value, "date")
        self.assertEqual(TrafficHourSummaryBBIPField.TIME.value, "time")
        self.assertEqual(TrafficHourSummaryBBIPField.IN_PROM.value, "inProm")
        self.assertEqual(TrafficHourSummaryBBIPField.OUT_PROM.value, "outProm")
        self.assertEqual(TrafficHourSummaryBBIPField.IN_MAX.value, "inMax")
        self.assertEqual(TrafficHourSummaryBBIPField.OUT_MAX.value, "outMax")
        self.assertEqual(TrafficHourSummaryBBIPField.USE.value, "use")
        self.assertEqual(TrafficHourSummaryBBIPField.DEVICE.value, "id_source")


class TestTrafficHourSummaryBBIPEntity(unittest.TestCase):
    """Unit tests for the TrafficHourSummaryBBIPEntity model."""

    def test_creates_entity_with_valid_data(self) -> None:
        """A complete and well-typed payload must build a valid entity."""
        entity = TrafficHourSummaryBBIPEntity(
            date=date(2026, 1, 1),
            time=time(13, 0, 0),
            in_prom=1.0,
            in_max=2.0,
            out_prom=1.5,
            out_max=2.5,
            use=50.0,
            device=ObjectId(),
        )
        self.assertEqual(entity.time, time(13, 0, 0))
        self.assertEqual(entity.use, 50.0)

    def test_missing_required_field_raises_validation_error(self) -> None:
        """Omitting a required field must raise a pydantic ValidationError."""
        with self.assertRaises(ValidationError):
            TrafficHourSummaryBBIPEntity(
                date=date(2026, 1, 1),
                in_prom=1.0,
                in_max=2.0,
                out_prom=1.5,
                device=ObjectId(),
            )


if __name__ == "__main__":
    unittest.main()
