from pathlib import Path
from datetime import date, datetime, timedelta
from scanbackup.infrastructure import (
    MongoTrafficSourceBBIPRepository,
    MongoTrafficDailySummaryBBIPRepository,
    ExcelTrafficReportBBIPExporter,
)
from scanbackup.application.use_case.bbip.reports.daily_traffic import (
    TrafficDailyReportGeneratorUseCase,
)
from scanbackup.application.use_case.bbip.reports.monthly_traffic import (
    TrafficMonthlyReportGeneratorUseCase,
)
from scanbackup.application.use_case.bbip.reports.weekly_traffic import (
    TrafficWeeklyReportGeneratorUseCase,
)
from scanbackup.application.use_case.bbip.reports.biweekly_traffic import (
    TrafficBiweeklyReportGeneratorUseCase,
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
            report_exporter=ExcelTrafficReportBBIPExporter(),
            layers=layers,
            data_date=date_str,
            filename=filename,
            output_dir=Path(output_dir) if output_dir else None,
        )

        return use_case.execute()


class TrafficMonthlyReportGenerator:
    @staticmethod
    def execute(
        month_str: str | None = None,
        literal: bool = False,
        output_dir: str | None = None,
    ) -> str:
        """Generate the monthly traffic report of every active interface, grouped by layer, into a single .xlsx file.

        Args:
            month_str (str | None): The month to report, formatted as YYYY-MM.
                Defaults to the current month when omitted. Ignored when literal is True.
            literal (bool): When False (default), the period runs from the
                1st through the last day of the target month. When True, the
                period is the 30 trailing days counting back from today, inclusive.
            output_dir (str | None): Directory where the resulting .xlsx file
                is written. Defaults to the writer's built-in directory when omitted.

        Returns:
            str: The absolute path of the generated .xlsx file.
        """
        system = Configuration()
        layers = system.get_cfg_layers().bbip.names
        cfg_reports = system.get_cfg_metadata().reports

        if literal:
            today = date.today()
            start_date, end_date = TrafficMonthlyReportGeneratorUseCase.resolve_literal_range(
                today
            )
            filename = f"{cfg_reports.preffix_name}_{start_date}_{end_date}"
            use_case = TrafficMonthlyReportGeneratorUseCase(
                source_repository=MongoTrafficSourceBBIPRepository(),
                daily_repository=MongoTrafficDailySummaryBBIPRepository(),
                report_exporter=ExcelTrafficReportBBIPExporter(),
                layers=layers,
                filename=filename,
                literal=True,
                reference_date=today,
                output_dir=Path(output_dir) if output_dir else None,
            )
            return use_case.execute()

        if not month_str:
            today = date.today()
            year, month = today.year, today.month
        else:
            target = datetime.strptime(month_str, "%Y-%m")
            year, month = target.year, target.month

        filename = f"{cfg_reports.preffix_name}_{year:04d}-{month:02d}"

        use_case = TrafficMonthlyReportGeneratorUseCase(
            source_repository=MongoTrafficSourceBBIPRepository(),
            daily_repository=MongoTrafficDailySummaryBBIPRepository(),
            report_exporter=ExcelTrafficReportBBIPExporter(),
            layers=layers,
            year=year,
            month=month,
            filename=filename,
            output_dir=Path(output_dir) if output_dir else None,
        )

        return use_case.execute()


class TrafficWeeklyReportGenerator:
    @staticmethod
    def execute(literal: bool = False, output_dir: str | None = None) -> str:
        """Generate the weekly traffic report of every active interface, grouped by layer, into a single .xlsx file.

        Args:
            literal (bool): When False (default), the week runs from the
                Monday of the week before today's week (Sunday-first) through
                that week's Sunday. When True, the week is the 7 trailing
                days counting back from today, inclusive.
            output_dir (str | None): Directory where the resulting .xlsx file
                is written. Defaults to the writer's built-in directory when omitted.

        Returns:
            str: The absolute path of the generated .xlsx file.
        """
        today = date.today()
        start_date, end_date = TrafficWeeklyReportGeneratorUseCase.resolve_week_range(
            today, literal
        )

        system = Configuration()
        layers = system.get_cfg_layers().bbip.names
        cfg_reports = system.get_cfg_metadata().reports
        filename = f"{cfg_reports.preffix_name}_{start_date}_{end_date}"

        use_case = TrafficWeeklyReportGeneratorUseCase(
            source_repository=MongoTrafficSourceBBIPRepository(),
            daily_repository=MongoTrafficDailySummaryBBIPRepository(),
            report_exporter=ExcelTrafficReportBBIPExporter(),
            layers=layers,
            reference_date=today,
            filename=filename,
            literal=literal,
            output_dir=Path(output_dir) if output_dir else None,
        )

        return use_case.execute()


class TrafficBiweeklyReportGenerator:
    @staticmethod
    def execute(
        month_str: str | None = None,
        literal: bool = False,
        output_dir: str | None = None,
    ) -> str:
        """Generate the biweekly traffic report of every active interface, grouped by layer, into a single .xlsx file.

        Args:
            month_str (str | None): The month to report, formatted as YYYY-MM.
                Defaults to the current month when omitted. Ignored when literal is True.
            literal (bool): When False (default), the period runs from the
                1st through the 15th of the target month. When True, the
                period is the 15 trailing days counting back from today, inclusive.
            output_dir (str | None): Directory where the resulting .xlsx file
                is written. Defaults to the writer's built-in directory when omitted.

        Returns:
            str: The absolute path of the generated .xlsx file.
        """
        if literal:
            reference_date = date.today()
        elif not month_str:
            today = date.today()
            reference_date = date(today.year, today.month, 1)
        else:
            target = datetime.strptime(month_str, "%Y-%m")
            reference_date = date(target.year, target.month, 1)

        start_date, end_date = TrafficBiweeklyReportGeneratorUseCase.resolve_biweekly_range(
            reference_date, literal
        )

        system = Configuration()
        layers = system.get_cfg_layers().bbip.names
        cfg_reports = system.get_cfg_metadata().reports
        filename = f"{cfg_reports.preffix_name}_{start_date}_{end_date}"

        use_case = TrafficBiweeklyReportGeneratorUseCase(
            source_repository=MongoTrafficSourceBBIPRepository(),
            daily_repository=MongoTrafficDailySummaryBBIPRepository(),
            report_exporter=ExcelTrafficReportBBIPExporter(),
            layers=layers,
            reference_date=reference_date,
            filename=filename,
            literal=literal,
            output_dir=Path(output_dir) if output_dir else None,
        )

        return use_case.execute()
