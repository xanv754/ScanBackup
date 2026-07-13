from datetime import date, timedelta
from scanbackup.infrastructure import (
    MongoTrafficHistoryBBIPRepository,
    MongoTrafficSourceBBIPRepository,
    MongoTrafficDailySummaryBBIPRepository,
    MongoTrafficHourSummaryBBIPRepository,
    MongoIPHistoryBBIPRepository,
    MongoIPSourceBBIPRepository,
    MongoIPDailySummaryBBIPRepository,
    MongoIPHourSummaryBBIPRepository,
)
from scanbackup.application.use_case.bbip.updaters.traffic_summary import (
    TrafficSummaryGeneratorUseCase,
)
from scanbackup.application.use_case.bbip.updaters.ip_summary import (
    IPSummaryGeneratorUseCase,
)
from scanbackup.application.use_case.bbip.updaters.traffic_hour_summary import (
    TrafficHourSummaryGeneratorUseCase,
)
from scanbackup.application.use_case.bbip.updaters.ip_hour_summary import (
    IPHourSummaryGeneratorUseCase,
)
from scanbackup.shared import Configuration


class TrafficSummaryUpdater:
    @staticmethod
    def execute(date_str: str | None = None) -> None:
        """Generate the daily traffic summary of every layer from its stored history.

        Args:
            date_str (str | None): The day to summarize, formatted as YYYY-MM-DD.
                Defaults to yesterday when omitted.
        """
        if not date_str:
            yesterday = date.today() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")

        layers = Configuration().get_cfg_layers().bbip.names

        use_case = TrafficSummaryGeneratorUseCase(
            source_repository=MongoTrafficSourceBBIPRepository(),
            history_repository_factory=MongoTrafficHistoryBBIPRepository,
            daily_repository=MongoTrafficDailySummaryBBIPRepository(),
            layers=layers,
            data_date=date_str,
        )

        use_case.execute()


class IPSummaryUpdater:
    @staticmethod
    def execute(date_str: str | None = None) -> None:
        """Generate the daily active-IP summary of every layer from its stored history.

        Args:
            date_str (str | None): The day to summarize, formatted as YYYY-MM-DD.
                Defaults to yesterday when omitted.
        """
        if not date_str:
            yesterday = date.today() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")

        layers = Configuration().get_cfg_layers().ip.names

        use_case = IPSummaryGeneratorUseCase(
            source_repository=MongoIPSourceBBIPRepository(),
            history_repository_factory=MongoIPHistoryBBIPRepository,
            daily_repository=MongoIPDailySummaryBBIPRepository(),
            layers=layers,
            data_date=date_str,
        )

        use_case.execute()


class TrafficHourSummaryUpdater:
    @staticmethod
    def execute(date_str: str | None = None) -> None:
        """Generate the hourly traffic summary of every layer from its stored history.

        Args:
            date_str (str | None): The day to summarize, formatted as YYYY-MM-DD.
                Defaults to yesterday when omitted.
        """
        if not date_str:
            yesterday = date.today() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")

        layers = Configuration().get_cfg_layers().bbip.names

        use_case = TrafficHourSummaryGeneratorUseCase(
            source_repository=MongoTrafficSourceBBIPRepository(),
            history_repository_factory=MongoTrafficHistoryBBIPRepository,
            hour_repository=MongoTrafficHourSummaryBBIPRepository(),
            layers=layers,
            data_date=date_str,
        )

        use_case.execute()


class IPHourSummaryUpdater:
    @staticmethod
    def execute(date_str: str | None = None) -> None:
        """Generate the hourly active-IP summary of every layer from its stored history.

        Args:
            date_str (str | None): The day to summarize, formatted as YYYY-MM-DD.
                Defaults to yesterday when omitted.
        """
        if not date_str:
            yesterday = date.today() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")

        layers = Configuration().get_cfg_layers().ip.names

        use_case = IPHourSummaryGeneratorUseCase(
            source_repository=MongoIPSourceBBIPRepository(),
            history_repository_factory=MongoIPHistoryBBIPRepository,
            hour_repository=MongoIPHourSummaryBBIPRepository(),
            layers=layers,
            data_date=date_str,
        )

        use_case.execute()
