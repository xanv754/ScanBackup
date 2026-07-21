import unittest
from scanbackup.domain.repositories.bbip.summaries.traffic import (
    TrafficDailySummaryBBIPRepository,
    TrafficHourSummaryBBIPRepository,
)


class TestTrafficDailySummaryBBIPRepository(unittest.TestCase):
    """Unit tests for the TrafficDailySummaryBBIPRepository abstract interface."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with unimplemented abstract methods must not be instantiable."""
        with self.assertRaises(TypeError):
            TrafficDailySummaryBBIPRepository()

    def test_incomplete_subclass_cannot_be_instantiated(self) -> None:
        """A subclass missing an abstract method override must fail too."""

        class IncompleteRepository(TrafficDailySummaryBBIPRepository):
            def insert(self, data):
                return None

        with self.assertRaises(TypeError):
            IncompleteRepository()

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """A subclass implementing every abstract method must be instantiable."""

        class CompleteRepository(TrafficDailySummaryBBIPRepository):
            def insert(self, data):
                return None

            def get_by_date(self, target_date):
                return []

            def get_by_date_range(self, start_date, end_date):
                return []

        self.assertIsInstance(
            CompleteRepository(), TrafficDailySummaryBBIPRepository
        )


class TestTrafficHourSummaryBBIPRepository(unittest.TestCase):
    """Unit tests for the TrafficHourSummaryBBIPRepository abstract interface."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with unimplemented abstract methods must not be instantiable."""
        with self.assertRaises(TypeError):
            TrafficHourSummaryBBIPRepository()

    def test_incomplete_subclass_cannot_be_instantiated(self) -> None:
        """A subclass missing an abstract method override must fail too."""

        class IncompleteRepository(TrafficHourSummaryBBIPRepository):
            pass

        with self.assertRaises(TypeError):
            IncompleteRepository()

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """A subclass implementing every abstract method must be instantiable."""

        class CompleteRepository(TrafficHourSummaryBBIPRepository):
            def insert(self, data):
                return None

        self.assertIsInstance(CompleteRepository(), TrafficHourSummaryBBIPRepository)


if __name__ == "__main__":
    unittest.main()
