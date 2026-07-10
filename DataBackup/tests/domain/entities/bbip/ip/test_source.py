import unittest
from scanbackup.domain.entities.bbip.ip.source import IPSourceBBIPField


class TestIPSourceBBIPField(unittest.TestCase):
    """Unit tests for the IPSourceBBIPField enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(IPSourceBBIPField.LINK.value, "link")
        self.assertEqual(IPSourceBBIPField.DEVICE.value, "device")
        self.assertEqual(IPSourceBBIPField.STATUS.value, "status")
        self.assertEqual(IPSourceBBIPField.LAYER.value, "layer")


if __name__ == "__main__":
    unittest.main()
