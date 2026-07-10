import unittest
from scanbackup.domain.entities.bbip.ip.summaries.daily import (
    IPDailySummaryBBIPField,
)


class TestIPDailySummaryBBIPField(unittest.TestCase):
    """Unit tests for the IPDailySummaryBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(IPDailySummaryBBIPField.DATE.value, "date")
        self.assertEqual(IPDailySummaryBBIPField.IN_PROM.value, "inProm")
        self.assertEqual(IPDailySummaryBBIPField.IN_MAX.value, "inMax")
        self.assertEqual(IPDailySummaryBBIPField.DEVICE.value, "id_source")


if __name__ == "__main__":
    unittest.main()
