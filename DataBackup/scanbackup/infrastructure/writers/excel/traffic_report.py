from pathlib import Path
from scanbackup.domain import (
    TrafficReportBBIPExporter,
    TrafficDailyReportBBIPField,
    TrafficDailyReportBBIPEntity,
)
from scanbackup.infrastructure.writers.excel.export import ExcelWriter


class ExcelTrafficReportBBIPExporter(TrafficReportBBIPExporter):
    def export(
        self,
        rows: list[TrafficDailyReportBBIPEntity],
        layers: list[str],
        filename: str,
        output_dir: Path | None,
    ) -> str:
        """Export report rows into a single .xlsx file, with one sheet per uppercased layer."""
        writer = ExcelWriter(dir=output_dir)
        return writer.export(
            filename=filename,
            data=rows,
            model=TrafficDailyReportBBIPEntity,
            sheet_field=TrafficDailyReportBBIPField.LAYER.value,
            sheet_names=[layer.upper() for layer in layers],
            exclude={TrafficDailyReportBBIPField.LAYER.value},
        )
