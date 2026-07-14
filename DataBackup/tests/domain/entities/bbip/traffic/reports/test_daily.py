import unittest
from datetime import date
from pydantic import ValidationError
from scanbackup.domain.entities.bbip.traffic.reports.daily import (
    TrafficDailyReportBBIPField,
    TrafficDailyReportBBIPEntity,
)


class TestTrafficDailyReportBBIPField(unittest.TestCase):
    """Unit tests for the TrafficDailyReportBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(TrafficDailyReportBBIPField.INTERFACE.value, "interface")
        self.assertEqual(TrafficDailyReportBBIPField.MODEL.value, "model")
        self.assertEqual(TrafficDailyReportBBIPField.CAPACITY.value, "capacity")
        self.assertEqual(TrafficDailyReportBBIPField.LAYER.value, "layer")
        self.assertEqual(TrafficDailyReportBBIPField.DATE.value, "date")
        self.assertEqual(TrafficDailyReportBBIPField.IN_PROM.value, "in_prom")
        self.assertEqual(TrafficDailyReportBBIPField.IN_MAX.value, "in_max")
        self.assertEqual(TrafficDailyReportBBIPField.OUT_PROM.value, "out_prom")
        self.assertEqual(TrafficDailyReportBBIPField.OUT_MAX.value, "out_max")
        self.assertEqual(TrafficDailyReportBBIPField.USE.value, "use")


class TestTrafficDailyReportBBIPEntity(unittest.TestCase):
    """Unit tests for the TrafficDailyReportBBIPEntity model."""

    def _payload(self, **overrides) -> dict:
        """Build a valid entity payload, allowing individual field overrides."""
        payload = {
            "interface": "Gi0/0/0",
            "model": "Cisco",
            "capacity": 1000.0,
            "layer": "BORDE",
            "date": date(2026, 1, 1),
            "in_prom": 1.0,
            "in_max": 2.0,
            "out_prom": 1.5,
            "out_max": 2.5,
            "use": 50.0,
        }
        payload.update(overrides)
        return payload

    def test_creates_entity_with_valid_data(self) -> None:
        """A complete and well-typed payload must build a valid entity."""
        entity = TrafficDailyReportBBIPEntity(**self._payload())
        self.assertEqual(entity.interface, "Gi0/0/0")
        self.assertEqual(entity.use, 50.0)

    def test_missing_required_field_raises_validation_error(self) -> None:
        """Omitting a required field must raise a pydantic ValidationError."""
        payload = self._payload()
        del payload["capacity"]
        with self.assertRaises(ValidationError):
            TrafficDailyReportBBIPEntity(**payload)


if __name__ == "__main__":
    unittest.main()
