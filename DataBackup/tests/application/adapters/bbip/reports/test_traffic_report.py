import unittest
from unittest.mock import MagicMock, patch
from scanbackup.application.adapters.bbip.reports.traffic_report import (
    export_traffic_report,
)
from scanbackup.domain import TrafficDailyReportBBIPField

MODULE = "scanbackup.application.adapters.bbip.reports.traffic_report"


class TestExportTrafficReport(unittest.TestCase):
    """Unit tests for export_traffic_report."""

    @patch(f"{MODULE}.ExcelWriter")
    def test_uppercases_layers_and_delegates_to_the_writer(
        self, mock_writer_cls
    ) -> None:
        """Layers in any casing must be uppercased before being passed as sheet_names."""
        writer = MagicMock()
        writer.export.return_value = "/tmp/report.xlsx"
        mock_writer_cls.return_value = writer

        result = export_traffic_report(
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
