from bson import ObjectId
from scanbackup.infrastructure.readers.csv.summaries.database import (
    TrafficDailySummaryBBIPImport,
    IPDailySummaryBBIPImport,
    TrafficHourSummaryBBIPImport,
    IPHourSummaryBBIPImport,
)
from scanbackup.shared import FileEmptyError, DataContentError
from tests.support import TempDirTestCase


class TestTrafficDailySummaryBBIPImport(TempDirTestCase):
    """Unit tests for the TrafficDailySummaryBBIPImport CSV reader."""

    def test_imports_a_valid_row_and_drops_id(self) -> None:
        """A well-formed row must be parsed and its '_id' column discarded."""
        device_id = str(ObjectId())
        filepath = self.tmp_dir / "summary.csv"
        filepath.write_text(
            f"_id;date;inProm;outProm;inMax;outMax;use;id_source\n"
            f"x;2026-01-01;1.0;1.5;2.0;2.5;80.0;{device_id}\n",
            encoding="utf-8",
        )

        reader = TrafficDailySummaryBBIPImport(delimiter=";")
        rows = reader.import_data(filepath)

        self.assertEqual(len(rows), 1)
        self.assertNotIn("_id", rows[0])
        self.assertEqual(rows[0]["id_source"], ObjectId(device_id))
        self.assertEqual(rows[0]["use"], 80.0)

    def test_empty_file_raises_file_empty_error(self) -> None:
        """An empty file must raise FileEmptyError."""
        filepath = self.tmp_dir / "empty.csv"
        filepath.write_text("", encoding="utf-8")

        reader = TrafficDailySummaryBBIPImport(delimiter=";")
        with self.assertRaises(FileEmptyError):
            reader.import_data(filepath)

    def test_invalid_device_id_raises_data_content_error(self) -> None:
        """A malformed device id must raise DataContentError."""
        filepath = self.tmp_dir / "summary.csv"
        filepath.write_text(
            "date;inProm;outProm;inMax;outMax;use;id_source\n"
            "2026-01-01;1.0;1.5;2.0;2.5;80.0;not-an-object-id\n",
            encoding="utf-8",
        )

        reader = TrafficDailySummaryBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(filepath)

    def test_invalid_use_value_raises_data_content_error(self) -> None:
        """A non-numeric 'use' value must raise DataContentError."""
        device_id = str(ObjectId())
        filepath = self.tmp_dir / "summary.csv"
        filepath.write_text(
            f"date;inProm;outProm;inMax;outMax;use;id_source\n"
            f"2026-01-01;1.0;1.5;2.0;2.5;not-a-number;{device_id}\n",
            encoding="utf-8",
        )

        reader = TrafficDailySummaryBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(filepath)


class TestIPDailySummaryBBIPImport(TempDirTestCase):
    """Unit tests for the IPDailySummaryBBIPImport CSV reader."""

    def test_imports_a_valid_row(self) -> None:
        """A well-formed row must be parsed into ObjectId/float typed values."""
        device_id = str(ObjectId())
        filepath = self.tmp_dir / "ip_summary.csv"
        filepath.write_text(
            f"date;inProm;inMax;id_source\n2026-01-01;1.0;2.0;{device_id}\n",
            encoding="utf-8",
        )

        reader = IPDailySummaryBBIPImport(delimiter=";")
        rows = reader.import_data(filepath)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id_source"], ObjectId(device_id))

    def test_empty_file_raises_file_empty_error(self) -> None:
        """An empty file must raise FileEmptyError."""
        filepath = self.tmp_dir / "empty.csv"
        filepath.write_text("", encoding="utf-8")

        reader = IPDailySummaryBBIPImport(delimiter=";")
        with self.assertRaises(FileEmptyError):
            reader.import_data(filepath)

    def test_invalid_device_id_raises_data_content_error(self) -> None:
        """A malformed device id must raise DataContentError."""
        filepath = self.tmp_dir / "ip_summary.csv"
        filepath.write_text(
            "date;inProm;inMax;id_source\n2026-01-01;1.0;2.0;not-an-object-id\n",
            encoding="utf-8",
        )

        reader = IPDailySummaryBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(filepath)


class TestTrafficHourSummaryBBIPImport(TempDirTestCase):
    """Unit tests for the TrafficHourSummaryBBIPImport CSV reader."""

    def test_imports_a_valid_row_and_drops_id(self) -> None:
        """A well-formed row must be parsed and its '_id' column discarded."""
        device_id = str(ObjectId())
        filepath = self.tmp_dir / "summary.csv"
        filepath.write_text(
            f"_id;date;time;inProm;outProm;inMax;outMax;use;id_source\n"
            f"x;2026-01-01;13:00:00;1.0;1.5;2.0;2.5;80.0;{device_id}\n",
            encoding="utf-8",
        )

        reader = TrafficHourSummaryBBIPImport(delimiter=";")
        rows = reader.import_data(filepath)

        self.assertEqual(len(rows), 1)
        self.assertNotIn("_id", rows[0])
        self.assertEqual(rows[0]["time"], "13:00:00")
        self.assertEqual(rows[0]["id_source"], ObjectId(device_id))
        self.assertEqual(rows[0]["use"], 80.0)

    def test_empty_file_raises_file_empty_error(self) -> None:
        """An empty file must raise FileEmptyError."""
        filepath = self.tmp_dir / "empty.csv"
        filepath.write_text("", encoding="utf-8")

        reader = TrafficHourSummaryBBIPImport(delimiter=";")
        with self.assertRaises(FileEmptyError):
            reader.import_data(filepath)

    def test_invalid_device_id_raises_data_content_error(self) -> None:
        """A malformed device id must raise DataContentError."""
        filepath = self.tmp_dir / "summary.csv"
        filepath.write_text(
            "date;time;inProm;outProm;inMax;outMax;use;id_source\n"
            "2026-01-01;13:00:00;1.0;1.5;2.0;2.5;80.0;not-an-object-id\n",
            encoding="utf-8",
        )

        reader = TrafficHourSummaryBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(filepath)

    def test_invalid_use_value_raises_data_content_error(self) -> None:
        """A non-numeric 'use' value must raise DataContentError."""
        device_id = str(ObjectId())
        filepath = self.tmp_dir / "summary.csv"
        filepath.write_text(
            f"date;time;inProm;outProm;inMax;outMax;use;id_source\n"
            f"2026-01-01;13:00:00;1.0;1.5;2.0;2.5;not-a-number;{device_id}\n",
            encoding="utf-8",
        )

        reader = TrafficHourSummaryBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(filepath)


class TestIPHourSummaryBBIPImport(TempDirTestCase):
    """Unit tests for the IPHourSummaryBBIPImport CSV reader."""

    def test_imports_a_valid_row(self) -> None:
        """A well-formed row must be parsed into ObjectId/float typed values."""
        device_id = str(ObjectId())
        filepath = self.tmp_dir / "ip_summary.csv"
        filepath.write_text(
            f"date;time;inProm;inMax;id_source\n2026-01-01;13:00:00;1.0;2.0;{device_id}\n",
            encoding="utf-8",
        )

        reader = IPHourSummaryBBIPImport(delimiter=";")
        rows = reader.import_data(filepath)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["time"], "13:00:00")
        self.assertEqual(rows[0]["id_source"], ObjectId(device_id))

    def test_empty_file_raises_file_empty_error(self) -> None:
        """An empty file must raise FileEmptyError."""
        filepath = self.tmp_dir / "empty.csv"
        filepath.write_text("", encoding="utf-8")

        reader = IPHourSummaryBBIPImport(delimiter=";")
        with self.assertRaises(FileEmptyError):
            reader.import_data(filepath)

    def test_invalid_device_id_raises_data_content_error(self) -> None:
        """A malformed device id must raise DataContentError."""
        filepath = self.tmp_dir / "ip_summary.csv"
        filepath.write_text(
            "date;time;inProm;inMax;id_source\n2026-01-01;13:00:00;1.0;2.0;not-an-object-id\n",
            encoding="utf-8",
        )

        reader = IPHourSummaryBBIPImport(delimiter=";")
        with self.assertRaises(DataContentError):
            reader.import_data(filepath)


if __name__ == "__main__":
    import unittest

    unittest.main()
