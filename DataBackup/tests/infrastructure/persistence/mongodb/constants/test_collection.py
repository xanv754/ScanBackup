import unittest
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
    SuffixCollectionName,
)


class TestMongoCollectionName(unittest.TestCase):
    """Unit tests for the MongoCollectionName enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw collection name."""
        self.assertEqual(MongoCollectionName.TRAFFIC_SOURCES.value, "TRAFFIC_SOURCE_BBIP")
        self.assertEqual(MongoCollectionName.IP_SOURCES.value, "IP_SOURCE_BBIP")
        self.assertEqual(
            MongoCollectionName.TRAFFIC_DAILY_SUMMARY.value, "TRAFFIC_DAILY_SUMMARY_BBIP"
        )
        self.assertEqual(
            MongoCollectionName.IP_DAILY_SUMMARY.value, "IP_DAILY_SUMMARY_BBIP"
        )


class TestSuffixCollectionName(unittest.TestCase):
    """Unit tests for the SuffixCollectionName enum."""

    def test_field_values(self) -> None:
        """Each enum member must expose the expected raw suffix value."""
        self.assertEqual(SuffixCollectionName.TRAFFIC_HISTORIES.value, "TRAFFIC_HISTORY_BBIP")
        self.assertEqual(SuffixCollectionName.IP_HISTORIES.value, "IP_HISTORY_BBIP")


if __name__ == "__main__":
    unittest.main()
