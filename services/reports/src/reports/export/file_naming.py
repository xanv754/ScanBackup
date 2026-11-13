from datetime import datetime

from reports.report_config import ReportConfig


class ReportFileNamer:
    """Builds the name of the report file: `<prefix_name>_<date>.<extension>` [RF-042].

    The date is the moment the file is generated, formatted with `date_format`. The name does
    not include the requested range.
    """

    def __init__(self, config: ReportConfig) -> None:
        """Receive the validated report configuration."""
        self._config = config

    def file_name(self, generated_at: datetime, extension: str) -> str:
        """Return the file name for the moment of generation."""
        date_text = generated_at.strftime(self._config.date_format)
        return f"{self._config.prefix_name}_{date_text}{extension}"
