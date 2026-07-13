import unittest
from scanbackup.shared.constants.headers.traffic_bbip_source import (
    TrafficSourceBBIPHeader,
)
from scanbackup.shared.constants.headers.ip_bbip_source import IPSourceBBIPHeader


class TestTrafficSourceBBIPHeader(unittest.TestCase):
    """Unit tests for the TrafficSourceBBIPHeader enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(TrafficSourceBBIPHeader.LINK.value, "link")
        self.assertEqual(TrafficSourceBBIPHeader.INTERFACE.value, "enlace")
        self.assertEqual(TrafficSourceBBIPHeader.TYPE.value, "model")
        self.assertEqual(TrafficSourceBBIPHeader.CAPACITY.value, "capacidad")


class TestIPSourceBBIPHeader(unittest.TestCase):
    """Unit tests for the IPSourceBBIPHeader enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(IPSourceBBIPHeader.LINK.value, "link")
        self.assertEqual(IPSourceBBIPHeader.INTERFACE.value, "interface")


if __name__ == "__main__":
    unittest.main()
