import unittest
from scanbackup.shared.constants.headers.data_scan import SCANHeader
from scanbackup.shared.constants.headers.traffic_bbip_source import (
    TrafficSourceBBIPHeader,
)
from scanbackup.shared.constants.headers.traffic_bbip_history import (
    TrafficHistoryBBIPHeader,
)
from scanbackup.shared.constants.headers.traffic_bbip_daily_summary import (
    TrafficDailySummaryBBIPHeader,
)


class TestSCANHeader(unittest.TestCase):
    """Unit tests for the SCANHeader enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(SCANHeader.INTERFACE.value, "Interface")
        self.assertEqual(SCANHeader.CAPACITY.value, "Capacity")
        self.assertEqual(SCANHeader.MODEL.value, "Model")
        self.assertEqual(SCANHeader.DATE.value, "Date")
        self.assertEqual(SCANHeader.TIME.value, "Time")
        self.assertEqual(SCANHeader.IN_PROM.value, "In_Prom")
        self.assertEqual(SCANHeader.OUT_PROM.value, "Out_Prom")
        self.assertEqual(SCANHeader.IN_MAX.value, "In_Max")
        self.assertEqual(SCANHeader.OUT_MAX.value, "Out_Max")
        self.assertEqual(SCANHeader.LAYER.value, "Layer")


class TestTrafficSourceBBIPHeader(unittest.TestCase):
    """Unit tests for the TrafficSourceBBIPHeader enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(TrafficSourceBBIPHeader.LINK.value, "link")
        self.assertEqual(TrafficSourceBBIPHeader.INTERFACE.value, "enlace")
        self.assertEqual(TrafficSourceBBIPHeader.TYPE.value, "model")
        self.assertEqual(TrafficSourceBBIPHeader.CAPACITY.value, "capacidad")


class TestTrafficHistoryBBIPHeader(unittest.TestCase):
    """Unit tests for the TrafficHistoryBBIPHeader enum."""

    def test_reuses_scan_header_values(self) -> None:
        """History headers derived from SCANHeader must match its raw values."""
        self.assertEqual(TrafficHistoryBBIPHeader.DEVICE.value, "Device")
        self.assertEqual(TrafficHistoryBBIPHeader.INTERFACE.value, SCANHeader.INTERFACE.value)
        self.assertEqual(TrafficHistoryBBIPHeader.DATE.value, SCANHeader.DATE.value)
        self.assertEqual(TrafficHistoryBBIPHeader.LAYER.value, SCANHeader.LAYER.value)


class TestTrafficDailySummaryBBIPHeader(unittest.TestCase):
    """Unit tests for the TrafficDailySummaryBBIPHeader enum."""

    def test_reuses_scan_header_values(self) -> None:
        """Summary headers derived from SCANHeader must match its raw values."""
        self.assertEqual(TrafficDailySummaryBBIPHeader.DEVICE.value, "Device")
        self.assertEqual(TrafficDailySummaryBBIPHeader.USE.value, "Use")
        self.assertEqual(TrafficDailySummaryBBIPHeader.DATE.value, SCANHeader.DATE.value)
        self.assertEqual(TrafficDailySummaryBBIPHeader.IN_MAX.value, SCANHeader.IN_MAX.value)


if __name__ == "__main__":
    unittest.main()
