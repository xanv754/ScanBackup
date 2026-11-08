from traffic_collector.clock import TargetDate
from traffic_collector.domain.results import SummaryResult
from traffic_collector.reporting.events import EventSink, SummaryPending


class PendingSummaryPhase:
    """Placeholder of the daily summary while RF-026 is not specified.

    It reports that the summary is pending and never fails.
    """

    def __init__(self, event_sink: EventSink) -> None:
        """Receive the sink where the pending notice is published."""
        self._event_sink = event_sink

    def run(self, target_date: TargetDate) -> SummaryResult:
        """Publish the pending notice and return a successful result."""
        self._event_sink.publish(SummaryPending())
        return SummaryResult()
