from scanbackup.domain.entities.bbip.traffic.summaries.daily import (
    TrafficDailySummaryBBIPEntity,
)
from scanbackup.domain.entities.bbip.traffic.summaries.hour import (
    TrafficHourSummaryBBIPEntity,
)


class TrafficDailySummaryBBIPRepository:
    def insert(self, data: list[TrafficDailySummaryBBIPEntity]) -> None:
        pass


class TrafficHourSummaryBBIPRepository:
    def insert(self, data: list[TrafficHourSummaryBBIPEntity]) -> None:
        """Persist a batch of hourly traffic summaries."""
        pass
