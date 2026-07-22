import unittest
from pathlib import Path
from scanbackup.domain.ports.reader import BaseReader


class TestBaseReader(unittest.TestCase):
    """Unit tests for the BaseReader abstract interface."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with an unimplemented abstract method must not be instantiable."""
        with self.assertRaises(TypeError):
            BaseReader()

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """A subclass implementing import_data must be instantiable and usable."""

        class DummyReader(BaseReader):
            def import_data(self, filepath: Path) -> list[dict]:
                return [{"path": str(filepath)}]

        reader = DummyReader()
        self.assertEqual(reader.import_data(Path("a.csv")), [{"path": "a.csv"}])


if __name__ == "__main__":
    unittest.main()
