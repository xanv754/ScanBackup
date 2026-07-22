import unittest
from unittest.mock import MagicMock, patch
from scanbackup.infrastructure.writers.excel.traffic_report import (
    ExcelTrafficReportBBIPExporter,
)
from scanbackup.domain import TrafficDailyReportBBIPField

MODULE = "scanbackup.infrastructure.writers.excel.traffic_report"


class TestExcelTrafficReportBBIPExporter(unittest.TestCase):
    """Unit tests for ExcelTrafficReportBBIPExporter."""

    @patch(f"{MODULE}.ExcelWriter")
    def test_uppercases_layers_and_delegates_to_the_writer(
        self, mock_writer_cls
    ) -> None:
        """Layers in any casing must be uppercased before being passed as sheet_names."""
        writer = MagicMock()
        writer.export.return_value = "/tmp/report.xlsx"
        mock_writer_cls.return_value = writer

        result = ExcelTrafficReportBBIPExporter().export(
            rows=[], layers=["borde", "DINT"], filename="report", output_dir=None
        )

        self.assertEqual(result, "/tmp/report.xlsx")
        mock_writer_cls.assert_called_once_with(dir=None)
        self.assertEqual(
            writer.export.call_args.kwargs["sheet_names"], ["BORDE", "DINT"]
        )
        self.assertEqual(
            writer.export.call_args.kwargs["exclude"],
            {TrafficDailyReportBBIPField.LAYER.value},
        )


if __name__ == "__main__":
    unittest.main()
