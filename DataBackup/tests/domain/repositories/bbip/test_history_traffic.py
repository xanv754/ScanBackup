import unittest
from datetime import date
from scanbackup.domain.repositories.bbip.history.traffic import (
    TrafficHistoryBBIPRepository,
)


class TestTrafficHistoryBBIPRepository(unittest.TestCase):
    """Unit tests for the TrafficHistoryBBIPRepository interface."""

    def test_insert_is_a_no_op(self) -> None:
        """The base insert method must be callable and return nothing."""
        repository = TrafficHistoryBBIPRepository()
        result = repository.insert([])
        self.assertIsNone(result)

    def test_get_by_date_is_a_no_op(self) -> None:
        """The base get_by_date method must be callable and return nothing."""
        repository = TrafficHistoryBBIPRepository()
        result = repository.get_by_date(date(2026, 1, 1))
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
