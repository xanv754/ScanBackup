from abc import ABC, abstractmethod
from collections.abc import Sequence

from bson import ObjectId

from reports.domain.date_range import DateRange
from reports.domain.models import AggregatedSummary, InterfaceInfo


class InterfaceRepository(ABC):
    """Read access to the `interfaces` collection. Layer membership comes only from here."""

    @abstractmethod
    def layer_values(self) -> list[str]:
        """Return the distinct stored layer values, whatever the status of the interfaces.

        Raises `DatabaseError` if the database fails.
        """

    @abstractmethod
    def find_by_layer_values(self, stored_values: Sequence[str]) -> list[InterfaceInfo]:
        """Return the interfaces whose stored layer is any of `stored_values`, in any status.

        Raises `DatabaseError` if the database fails.
        """


class DailySummaryRepository(ABC):
    """Read access to the `traffic_summary_daily` collection. Values are in bps."""

    @abstractmethod
    def aggregate(
        self, interface_ids: Sequence[ObjectId], date_range: DateRange
    ) -> list[AggregatedSummary]:
        """Aggregate in the database the summaries of the interfaces inside the range.

        Returns the average of the daily averages, the maximum of the daily maximums and the
        number of days, for each interface that has at least one summary. Interfaces without
        summaries do not appear. Raises `DatabaseError` if the database fails.
        """

    @abstractmethod
    def dates_with_summary(
        self, interface_ids: Sequence[ObjectId], date_range: DateRange
    ) -> set[str]:
        """Return the distinct days of the range that have a summary for any of the interfaces.

        Raises `DatabaseError` if the database fails.
        """
