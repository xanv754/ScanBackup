import unittest
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


if __name__ == "__main__":
    unittest.main()
