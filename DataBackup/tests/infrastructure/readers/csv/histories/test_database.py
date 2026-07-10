from bson import ObjectId
from scanbackup.infrastructure.readers.csv.histories.database import (
    TrafficHistoryBBIPImport,
    IPHistoryBBIPImport,
)
from scanbackup.shared import FileEmptyError, DataContentError
from tests.support import TempDirTestCase


class TestTrafficHistoryBBIPImport(TempDirTestCase):
    """Unit tests for the TrafficHistoryBBIPImport CSV reader."""

    def test_imports_a_valid_row(self) -> None:
        """A well-formed row must be parsed into ObjectId/float typed values."""
        device_id = str(ObjectId())
        filepath = self.tmp_dir / "traffic.csv"
        filepath.write_text(
            f"date;time;inProm;inMax;outProm;outMax;id_source\n"
            f"2026-01-01;10:00:00;1.5;2.5;1.0;2.0;{device_id}\n",
            encoding="utf-8",
        )

        reader = TrafficHistoryBBIPImport(delimiter=";")
        rows = reader.import_data(filepath)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id_source"], ObjectId(device_id))
        self.assertEqual(rows[0]["inProm"], 1.5)

    def test_empty_file_raises_file_empty_error(self) -> None:
        """An empty file must raise FileEmptyError."""
        filepath = self.tmp_dir / "empty.csv"
        filepath.write_text("", encoding="utf-8")

        reader = TrafficHistoryBBIPImport(delimiter=";")
        with self.assertRaises(FileEmptyError):
            reader.import_data(filepath)

    def test_invalid_device_id_raises_data_content_error(self) -> None:
        """A malformed device id must raise DataContentError."""
        filepath = self.tmp_dir / "traffic.csv"
        filepath.write_text(
            "date;time;inProm;inMax;outProm;outMax;id_source\n"
            "2026-01-01;10:00:00;1.5;2.5;1.0;2.0;not-an-object-id\n",
            encoding="utf-8",
        )

        reader = TrafficHistoryBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(filepath)

    def test_invalid_float_value_raises_data_content_error(self) -> None:
        """A non-numeric traffic value must raise DataContentError."""
        device_id = str(ObjectId())
        filepath = self.tmp_dir / "traffic.csv"
        filepath.write_text(
            f"date;time;inProm;inMax;outProm;outMax;id_source\n"
            f"2026-01-01;10:00:00;not-a-number;2.5;1.0;2.0;{device_id}\n",
            encoding="utf-8",
        )

        reader = TrafficHistoryBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(filepath)


class TestIPHistoryBBIPImport(TempDirTestCase):
    """Unit tests for the IPHistoryBBIPImport CSV reader."""

    def test_imports_a_valid_row(self) -> None:
        """A well-formed row must be parsed into ObjectId/float typed values."""
        device_id = str(ObjectId())
        filepath = self.tmp_dir / "ip_history.csv"
        filepath.write_text(
            f"date;time;inProm;inMax;id_source\n"
            f"2026-01-01;10:00:00;1.5;2.5;{device_id}\n",
            encoding="utf-8",
        )

        reader = IPHistoryBBIPImport(delimiter=";")
        rows = reader.import_data(filepath)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id_source"], ObjectId(device_id))

    def test_empty_file_raises_file_empty_error(self) -> None:
        """An empty file must raise FileEmptyError."""
        filepath = self.tmp_dir / "empty.csv"
        filepath.write_text("", encoding="utf-8")

        reader = IPHistoryBBIPImport(delimiter=";")
        with self.assertRaises(FileEmptyError):
            reader.import_data(filepath)

    def test_invalid_device_id_raises_data_content_error(self) -> None:
        """A malformed device id must raise DataContentError."""
        filepath = self.tmp_dir / "ip_history.csv"
        filepath.write_text(
            "date;time;inProm;inMax;id_source\n"
            "2026-01-01;10:00:00;1.5;2.5;not-an-object-id\n",
            encoding="utf-8",
        )

        reader = IPHistoryBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(filepath)


if __name__ == "__main__":
    import unittest

    unittest.main()
