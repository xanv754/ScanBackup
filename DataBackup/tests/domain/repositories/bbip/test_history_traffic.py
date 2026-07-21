import unittest
from scanbackup.domain.repositories.bbip.history.traffic import (
    TrafficHistoryBBIPRepository,
)


class TestTrafficHistoryBBIPRepository(unittest.TestCase):
    """Unit tests for the TrafficHistoryBBIPRepository abstract interface."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with unimplemented abstract methods must not be instantiable."""
        with self.assertRaises(TypeError):
            TrafficHistoryBBIPRepository()

    def test_incomplete_subclass_cannot_be_instantiated(self) -> None:
        """A subclass missing an abstract method override must fail too."""

        class IncompleteRepository(TrafficHistoryBBIPRepository):
            def insert(self, data):
                return None

        with self.assertRaises(TypeError):
            IncompleteRepository()

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """A subclass implementing every abstract method must be instantiable."""

        class CompleteRepository(TrafficHistoryBBIPRepository):
            def insert(self, data):
                return None

            def get_by_date(self, target_date):
                return []

        self.assertIsInstance(CompleteRepository(), TrafficHistoryBBIPRepository)


if __name__ == "__main__":
    unittest.main()
