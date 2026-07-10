from scanbackup.infrastructure.readers.csv.sources.database import (
    TrafficSourceBBIPImport,
    IPSourceBBIPImport,
)
from scanbackup.shared import DataContentError
from tests.support import TempDirTestCase


class TestTrafficSourceBBIPImport(TempDirTestCase):
    """Unit tests for the TrafficSourceBBIPImport CSV reader."""

    def test_imports_valid_rows_and_converts_capacity(self) -> None:
        """A well-formed row must convert capacity to float and drop '_id'."""
        filepath = self.tmp_dir / "sources.csv"
        filepath.write_text(
            "_id;link;interface;capacity;model\n"
            "abc123;http://example.com;Gi0/0/0;100.5;Cisco\n",
            encoding="utf-8",
        )

        reader = TrafficSourceBBIPImport(delimiter=";")
        documents = reader.import_data(filepath)

        self.assertEqual(len(documents), 1)
        self.assertNotIn("_id", documents[0])
        self.assertEqual(documents[0]["capacity"], 100.5)

    def test_invalid_capacity_raises_data_content_error(self) -> None:
        """A non-numeric capacity value must raise DataContentError."""
        filepath = self.tmp_dir / "sources.csv"
        filepath.write_text(
            "link;interface;capacity;model\n"
            "http://example.com;Gi0/0/0;not-a-number;Cisco\n",
            encoding="utf-8",
        )

        reader = TrafficSourceBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(filepath)

    def test_missing_file_raises_data_content_error(self) -> None:
        """A missing input file must be wrapped into a DataContentError."""
        reader = TrafficSourceBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(self.tmp_dir / "missing.csv")


class TestIPSourceBBIPImport(TempDirTestCase):
    """Unit tests for the IPSourceBBIPImport CSV reader."""

    def test_imports_valid_rows_and_drops_id(self) -> None:
        """A well-formed row must be returned as a dict without the '_id' key."""
        filepath = self.tmp_dir / "ip_sources.csv"
        filepath.write_text(
            "_id;link;device;status;layer\n"
            "abc123;http://example.com;Gi0/0/0;ACTIVO;DINT\n",
            encoding="utf-8",
        )

        reader = IPSourceBBIPImport(delimiter=";")
        documents = reader.import_data(filepath)

        self.assertEqual(len(documents), 1)
        self.assertNotIn("_id", documents[0])
        self.assertEqual(documents[0]["device"], "Gi0/0/0")

    def test_missing_file_raises_data_content_error(self) -> None:
        """A missing input file must be wrapped into a DataContentError."""
        reader = IPSourceBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(self.tmp_dir / "missing.csv")


if __name__ == "__main__":
    import unittest

    unittest.main()
