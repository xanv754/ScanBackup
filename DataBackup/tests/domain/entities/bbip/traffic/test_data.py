import unittest
from datetime import date, time
from bson import ObjectId
from pydantic import ValidationError
from scanbackup.domain.entities.bbip.traffic.data import (
    TrafficBBIPField,
    TrafficBBIPEntity,
)


class TestTrafficBBIPField(unittest.TestCase):
    """Unit tests for the TrafficBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(TrafficBBIPField.DATE.value, "date")
        self.assertEqual(TrafficBBIPField.TIME.value, "time")
        self.assertEqual(TrafficBBIPField.IN_PROM.value, "inProm")
        self.assertEqual(TrafficBBIPField.IN_MAX.value, "inMax")
        self.assertEqual(TrafficBBIPField.OUT_PROM.value, "outProm")
        self.assertEqual(TrafficBBIPField.OUT_MAX.value, "outMax")
        self.assertEqual(TrafficBBIPField.DEVICE.value, "id_source")


class TestTrafficBBIPEntity(unittest.TestCase):
    """Unit tests for the TrafficBBIPEntity model."""

    def test_creates_entity_with_valid_data(self) -> None:
        """A complete and well-typed payload must build a valid entity."""
        entity = TrafficBBIPEntity(
            date=date(2026, 1, 1),
            time=time(10, 0),
            in_prom=1.5,
            in_max=2.5,
            out_prom=1.0,
            out_max=2.0,
            device=ObjectId(),
        )
        self.assertEqual(entity.in_prom, 1.5)
        self.assertEqual(entity.date, date(2026, 1, 1))

    def test_missing_required_field_raises_validation_error(self) -> None:
        """Omitting a required field must raise a pydantic ValidationError."""
        with self.assertRaises(ValidationError):
            TrafficBBIPEntity(
                date=date(2026, 1, 1),
                time=time(10, 0),
                in_prom=1.5,
                in_max=2.5,
                out_prom=1.0,
                device=ObjectId(),
            )


if __name__ == "__main__":
    unittest.main()
