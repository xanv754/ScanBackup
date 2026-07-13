import unittest
from scanbackup.domain.repositories.bbip.summaries.ip import (
    IPDailySummaryBBIPRepository,
    IPHourSummaryBBIPRepository,
)


class TestIPDailySummaryBBIPRepository(unittest.TestCase):
    """Unit tests for the IPDailySummaryBBIPRepository interface."""

    def test_insert_is_a_no_op(self) -> None:
        """The base insert method must be callable and return nothing."""
        repository = IPDailySummaryBBIPRepository()
        result = repository.insert([])
        self.assertIsNone(result)


class TestIPHourSummaryBBIPRepository(unittest.TestCase):
    """Unit tests for the IPHourSummaryBBIPRepository interface."""

    def test_insert_is_a_no_op(self) -> None:
        """The base insert method must be callable and return nothing."""
        repository = IPHourSummaryBBIPRepository()
        result = repository.insert([])
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
