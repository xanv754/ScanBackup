from pathlib import Path
from scanbackup.domain import TrafficDailyReportBBIPField, TrafficDailyReportBBIPEntity
from scanbackup.infrastructure import ExcelWriter


def export_traffic_report(
    rows: list[TrafficDailyReportBBIPEntity],
    layers: list[str],
    filename: str,
    output_dir: Path | None,
) -> str:
    """Export report rows into a single .xlsx file, with one sheet per uppercased layer.

    Args:
        rows (list[TrafficDailyReportBBIPEntity]): The rows to export.
        layers (list[str]): Every configured traffic layer, in any casing.
            Uppercased to match the stored source layer values. One Excel
            sheet is produced per layer, even when it has no rows.
        filename (str): Base name of the .xlsx file to create, without extension.
        output_dir (Path | None): Directory where the resulting .xlsx file is
            written. Defaults to the writer's built-in directory when omitted.

    Returns:
        str: The absolute path of the generated .xlsx file.
    """
    writer = ExcelWriter(dir=output_dir)
    return writer.export(
        filename=filename,
        data=rows,
        model=TrafficDailyReportBBIPEntity,
        sheet_field=TrafficDailyReportBBIPField.LAYER.value,
        sheet_names=[layer.upper() for layer in layers],
        exclude={TrafficDailyReportBBIPField.LAYER.value},
    )
