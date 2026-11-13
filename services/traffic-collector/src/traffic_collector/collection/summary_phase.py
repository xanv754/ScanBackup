from traffic_collector.clock import TargetDate
from traffic_collector.collection.protocols import SummaryWriter, TrafficReader
from traffic_collector.collection.summary_calculator import DailySummaryCalculator
from traffic_collector.domain.results import SummaryResult
from traffic_collector.exceptions import DatabaseError
from traffic_collector.reporting.events import EventSink, SummaryFailed, SummaryFinished


class DailySummaryPhase:
    """Generates the daily summary of every stored interface after the collection [RF-026].

    Interfaces that already have a summary, or have no samples, are skipped. A database error
    stops the phase, because the next interfaces would fail the same way.
    """

    def __init__(
        self,
        traffic_reader: TrafficReader,
        summary_writer: SummaryWriter,
        calculator: DailySummaryCalculator,
        event_sink: EventSink,
    ) -> None:
        """Receive the stores, the calculator and the sink for the events."""
        self._traffic_reader = traffic_reader
        self._summary_writer = summary_writer
        self._calculator = calculator
        self._event_sink = event_sink

    def run(self, target_date: TargetDate) -> SummaryResult:
        """Summarize every stored day of `target_date` and return the result."""
        generated_count = 0
        skipped_count = 0
        try:
            summarized_ids = self._summary_writer.interface_ids_with_summary(
                target_date.key
            )
            for daily_traffic in self._traffic_reader.daily_by_date(target_date.key):
                summary = self._calculator.calculate(daily_traffic)
                if summary is None or daily_traffic.interface_id in summarized_ids:
                    skipped_count += 1
                    continue
                self._summary_writer.save(summary)
                generated_count += 1
        except DatabaseError as error:
            self._event_sink.publish(SummaryFailed(generated_count, error))
            return SummaryResult(failed_count=1)
        self._event_sink.publish(SummaryFinished(generated_count, skipped_count))
        return SummaryResult()
