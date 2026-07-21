import unittest
from scanbackup.domain.repositories.bbip.history.ip import IPHistoryBBIPRepository


class TestIPHistoryBBIPRepository(unittest.TestCase):
    """Unit tests for the IPHistoryBBIPRepository abstract interface."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with unimplemented abstract methods must not be instantiable."""
        with self.assertRaises(TypeError):
            IPHistoryBBIPRepository()

    def test_incomplete_subclass_cannot_be_instantiated(self) -> None:
        """A subclass missing an abstract method override must fail too."""

        class IncompleteRepository(IPHistoryBBIPRepository):
            def insert(self, data):
                return None

        with self.assertRaises(TypeError):
            IncompleteRepository()

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """A subclass implementing every abstract method must be instantiable."""

        class CompleteRepository(IPHistoryBBIPRepository):
            def insert(self, data):
                return None

            def get_by_date(self, target_date):
                return []

        self.assertIsInstance(CompleteRepository(), IPHistoryBBIPRepository)


if __name__ == "__main__":
    unittest.main()
