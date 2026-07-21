import unittest
from scanbackup.domain.repositories.bbip.summaries.ip import (
    IPDailySummaryBBIPRepository,
    IPHourSummaryBBIPRepository,
)


class TestIPDailySummaryBBIPRepository(unittest.TestCase):
    """Unit tests for the IPDailySummaryBBIPRepository abstract interface."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with unimplemented abstract methods must not be instantiable."""
        with self.assertRaises(TypeError):
            IPDailySummaryBBIPRepository()

    def test_incomplete_subclass_cannot_be_instantiated(self) -> None:
        """A subclass missing an abstract method override must fail too."""

        class IncompleteRepository(IPDailySummaryBBIPRepository):
            pass

        with self.assertRaises(TypeError):
            IncompleteRepository()

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """A subclass implementing every abstract method must be instantiable."""

        class CompleteRepository(IPDailySummaryBBIPRepository):
            def insert(self, data):
                return None

        self.assertIsInstance(CompleteRepository(), IPDailySummaryBBIPRepository)


class TestIPHourSummaryBBIPRepository(unittest.TestCase):
    """Unit tests for the IPHourSummaryBBIPRepository abstract interface."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with unimplemented abstract methods must not be instantiable."""
        with self.assertRaises(TypeError):
            IPHourSummaryBBIPRepository()

    def test_incomplete_subclass_cannot_be_instantiated(self) -> None:
        """A subclass missing an abstract method override must fail too."""

        class IncompleteRepository(IPHourSummaryBBIPRepository):
            pass

        with self.assertRaises(TypeError):
            IncompleteRepository()

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """A subclass implementing every abstract method must be instantiable."""

        class CompleteRepository(IPHourSummaryBBIPRepository):
            def insert(self, data):
                return None

        self.assertIsInstance(CompleteRepository(), IPHourSummaryBBIPRepository)


if __name__ == "__main__":
    unittest.main()
