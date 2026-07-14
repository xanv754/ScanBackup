from pathlib import Path
from datetime import date, datetime, timedelta
from scanbackup.infrastructure import (
    MongoTrafficSourceBBIPRepository,
    MongoTrafficDailySummaryBBIPRepository,
)
from scanbackup.application.use_case.bbip.reports.daily_traffic import (
    TrafficDailyReportGeneratorUseCase,
)
from scanbackup.application.use_case.bbip.reports.monthly_traffic import (
    TrafficMonthlyReportGeneratorUseCase,
)
from scanbackup.shared import Configuration


class TrafficDailyReportGenerator:
    @staticmethod
    def execute(date_str: str | None = None, output_dir: str | None = None) -> str:
        """Generate the daily traffic report of every active interface, grouped by layer, into a single .xlsx file.

        Args:
            date_str (str | None): The day to report, formatted as YYYY-MM-DD.
                Defaults to yesterday when omitted.
            output_dir (str | None): Directory where the resulting .xlsx file
                is written. Defaults to the writer's built-in directory when omitted.

        Returns:
            str: The absolute path of the generated .xlsx file.
        """
        if not date_str:
            yesterday = date.today() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")

        system = Configuration()
        layers = system.get_cfg_layers().bbip.names
        cfg_reports = system.get_cfg_metadata().reports
        filename = f"{cfg_reports.preffix_name}_{date_str}"

        use_case = TrafficDailyReportGeneratorUseCase(
            source_repository=MongoTrafficSourceBBIPRepository(),
            daily_repository=MongoTrafficDailySummaryBBIPRepository(),
            layers=layers,
            data_date=date_str,
            filename=filename,
            output_dir=Path(output_dir) if output_dir else None,
        )

        return use_case.execute()


class TrafficMonthlyReportGenerator:
    @staticmethod
    def execute(month_str: str | None = None, output_dir: str | None = None) -> str:
        """Generate the monthly traffic report of every active interface, grouped by layer, into a single .xlsx file.

        Args:
            month_str (str | None): The month to report, formatted as YYYY-MM.
                Defaults to the current month when omitted.
            output_dir (str | None): Directory where the resulting .xlsx file
                is written. Defaults to the writer's built-in directory when omitted.

        Returns:
            str: The absolute path of the generated .xlsx file.
        """
        if not month_str:
            today = date.today()
            year, month = today.year, today.month
        else:
            target = datetime.strptime(month_str, "%Y-%m")
            year, month = target.year, target.month

        system = Configuration()
        layers = system.get_cfg_layers().bbip.names
        cfg_reports = system.get_cfg_metadata().reports
        filename = f"{cfg_reports.preffix_name}_{year:04d}-{month:02d}"

        use_case = TrafficMonthlyReportGeneratorUseCase(
            source_repository=MongoTrafficSourceBBIPRepository(),
            daily_repository=MongoTrafficDailySummaryBBIPRepository(),
            layers=layers,
            year=year,
            month=month,
            filename=filename,
            output_dir=Path(output_dir) if output_dir else None,
        )

        return use_case.execute()
