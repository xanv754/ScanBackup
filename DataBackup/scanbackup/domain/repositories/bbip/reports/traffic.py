from abc import ABC, abstractmethod
from pathlib import Path
from scanbackup.domain.entities.bbip.traffic.reports.daily import (
    TrafficDailyReportBBIPEntity,
)


class TrafficReportBBIPExporter(ABC):
    @abstractmethod
    def export(
        self,
        rows: list[TrafficDailyReportBBIPEntity],
        layers: list[str],
        filename: str,
        output_dir: Path | None,
    ) -> str:
        """Export report rows into a single file, with one sheet/section per uppercased layer.

        Args:
            rows (list[TrafficDailyReportBBIPEntity]): The rows to export.
            layers (list[str]): Every configured traffic layer, in any casing.
                Uppercased to match the stored source layer values. One
                section is produced per layer, even when it has no rows.
            filename (str): Base name of the file to create, without extension.
            output_dir (Path | None): Directory where the resulting file is
                written. Defaults to the writer's built-in directory when omitted.

        Returns:
            str: The absolute path of the generated file.
        """
        pass
