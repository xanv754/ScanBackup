import unittest
from scanbackup.shared.constants.types.device_status import SourceStatus


class TestSourceStatus(unittest.TestCase):
    """Unit tests for the SourceStatus enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw string value."""
        self.assertEqual(SourceStatus.ACTIVE.value, "ACTIVO")
        self.assertEqual(SourceStatus.DISCONTINUED.value, "DESINCORPORADO")


if __name__ == "__main__":
    unittest.main()
