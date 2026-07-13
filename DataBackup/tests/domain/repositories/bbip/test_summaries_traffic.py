import unittest
from scanbackup.domain.repositories.bbip.summaries.traffic import (
    TrafficDailySummaryBBIPRepository,
    TrafficHourSummaryBBIPRepository,
)


class TestTrafficDailySummaryBBIPRepository(unittest.TestCase):
    """Unit tests for the TrafficDailySummaryBBIPRepository interface."""

    def test_insert_is_a_no_op(self) -> None:
        """The base insert method must be callable and return nothing."""
        repository = TrafficDailySummaryBBIPRepository()
        result = repository.insert([])
        self.assertIsNone(result)


class TestTrafficHourSummaryBBIPRepository(unittest.TestCase):
    """Unit tests for the TrafficHourSummaryBBIPRepository interface."""

    def test_insert_is_a_no_op(self) -> None:
        """The base insert method must be callable and return nothing."""
        repository = TrafficHourSummaryBBIPRepository()
        result = repository.insert([])
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
