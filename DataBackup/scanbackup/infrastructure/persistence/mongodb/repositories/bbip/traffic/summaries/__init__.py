from scanbackup.infrastructure.persistence.mongodb.repositories.bbip.traffic.summaries.daily import (
    MongoTrafficDailySummaryBBIPRepository,
)
from scanbackup.infrastructure.persistence.mongodb.repositories.bbip.traffic.summaries.hour import (
    MongoTrafficHourSummaryBBIPRepository,
)

__all__ = [
    "MongoTrafficDailySummaryBBIPRepository",
    "MongoTrafficHourSummaryBBIPRepository",
]
