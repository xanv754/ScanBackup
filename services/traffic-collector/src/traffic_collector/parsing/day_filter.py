from traffic_collector.clock import TargetDate
from traffic_collector.domain import Sample


class DayFilter:
    """Keeps only the samples that belong to the target day in America/Caracas. Pure."""

    def __init__(self, target_date: TargetDate) -> None:
        """Receive the day to keep."""
        self._target_date = target_date

    def apply(self, samples: tuple[Sample, ...]) -> tuple[Sample, ...]:
        """Return the samples from 00:00:00 (included) to the next 00:00:00 (excluded) [RF-023].

        The values are not modified and the dates stay in UTC.
        """
        return tuple(sample for sample in samples if self._target_date.contains(sample.ts))
