from datetime import date
from scanbackup.domain.entities.bbip.traffic.data import TrafficBBIPEntity

class TrafficHistoryBBIPRepository:
    def insert(self, data: list[TrafficBBIPEntity]) -> None:
        pass

    def get_by_date(self, target_date: date) -> list[TrafficBBIPEntity]:
        """Retrieve every 5-minute traffic sample recorded on `target_date`."""
        pass
