import unittest
from scanbackup.domain.repositories.bbip.sources.ip import IPSourceBBIPRepository


class TestIPSourceBBIPRepository(unittest.TestCase):
    """Unit tests for the IPSourceBBIPRepository abstract interface."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with unimplemented abstract methods must not be instantiable."""
        with self.assertRaises(TypeError):
            IPSourceBBIPRepository()

    def test_incomplete_subclass_cannot_be_instantiated(self) -> None:
        """A subclass missing an abstract method override must fail too."""

        class IncompleteRepository(IPSourceBBIPRepository):
            def get_existing_keys(self):
                return []

        with self.assertRaises(TypeError):
            IncompleteRepository()

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """A subclass implementing every abstract method must be instantiable."""

        class CompleteRepository(IPSourceBBIPRepository):
            def get_existing_keys(self):
                return []

            def upsert_sources(self, data):
                return None

            def discontinue_missing(self, present_keys):
                return None

            def get_sources_by_layer(self, layer):
                return []

            def get_sources_by_layer_id(self, layer):
                return []

            def get_all_active_sources(self):
                return []

            def get_all_sources(self):
                return []

        self.assertIsInstance(CompleteRepository(), IPSourceBBIPRepository)


if __name__ == "__main__":
    unittest.main()
