import unittest
from pathlib import Path
from scanbackup.domain.ports.database import BaseDatabase


class TestBaseDatabase(unittest.TestCase):
    """Unit tests for the BaseDatabase abstract interface."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with unimplemented abstract methods must not be instantiable."""
        with self.assertRaises(TypeError):
            BaseDatabase()

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """A subclass implementing every abstract method must be instantiable and usable."""

        class DummyDatabase(BaseDatabase):
            def set_uri(self, config) -> None:
                self.uri = "dummy-uri"

            def create_collections(self, config) -> None:
                self.created = True

            def import_data(self, name_collection, config, input_filepath, delimiter) -> None:
                self.imported = name_collection

            def export_data(
                self, config, name_collection, dirpath: Path | None = None, include_id: bool = True
            ) -> str:
                return f"{dirpath}/{name_collection}.csv"

            def get_collection_names(self) -> list[str]:
                return ["a", "b"]

        database = DummyDatabase()
        database.set_uri(config=None)
        self.assertEqual(database.uri, "dummy-uri")
        self.assertEqual(database.get_collection_names(), ["a", "b"])
        self.assertEqual(
            database.export_data(config=None, name_collection="x", dirpath=Path("/tmp")),
            "/tmp/x.csv",
        )


if __name__ == "__main__":
    unittest.main()
