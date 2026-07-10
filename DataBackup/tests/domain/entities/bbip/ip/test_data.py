import unittest
from scanbackup.domain.entities.bbip.ip.data import IPActiveBBIPField


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


if __name__ == "__main__":
    unittest.main()
