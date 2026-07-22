import unittest
from datetime import date
from pydantic import BaseModel
from scanbackup.domain.ports.fetcher import BaseFetcher


class TestBaseFetcher(unittest.TestCase):
    """Unit tests for the BaseFetcher abstract interface."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with an unimplemented abstract method must not be instantiable."""
        with self.assertRaises(TypeError):
            BaseFetcher()

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """A subclass implementing fetch must be instantiable and usable."""

        class DummySource(BaseModel):
            link: str

        class DummyFetcher(BaseFetcher):
            def fetch(self, source: DummySource, target_date: date) -> list[BaseModel]:
                return [source]

        fetcher = DummyFetcher()
        source = DummySource(link="a.link")
        self.assertEqual(fetcher.fetch(source, date.today()), [source])


if __name__ == "__main__":
    unittest.main()
