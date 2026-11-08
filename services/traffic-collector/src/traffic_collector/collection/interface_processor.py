from traffic_collector.clock import TargetDate
from traffic_collector.collection.protocols import SummaryStore, TrafficStore
from traffic_collector.constants.enums import FailureCause, SampleCountVerdict
from traffic_collector.domain import ActiveInterface, DailyTraffic
from traffic_collector.domain.results import InterfaceResult
from traffic_collector.exceptions import DatabaseError
from traffic_collector.parsing import DayFilter, LogParser, SampleValidator
from traffic_collector.scan import ScanError


class InterfaceProcessor:
    """Turns the download of one interface into stored samples and a result.

    It never touches the network: it receives the downloaded text or the error. It runs
    parse -> filter -> validate -> store, and with `force` it first deletes the previous day.
    """

    def __init__(
        self,
        target_date: TargetDate,
        force: bool,
        parser: LogParser,
        day_filter: DayFilter,
        validator: SampleValidator,
        traffic_store: TrafficStore,
        summary_store: SummaryStore,
    ) -> None:
        """Receive the day, the force flag and every collaborator."""
        self._target_date = target_date
        self._force = force
        self._parser = parser
        self._day_filter = day_filter
        self._validator = validator
        self._traffic_store = traffic_store
        self._summary_store = summary_store

    def process(
        self, interface: ActiveInterface, layer: str, download: str | ScanError
    ) -> InterfaceResult:
        """Process one download and return the result of the interface [RF-022, RF-024].

        A `ScanError` fails the interface and nothing is deleted or stored. Zero valid samples
        of the target day also fail it. A database error while deleting or storing fails it with
        `STORAGE_ERROR`. Between 1-287 or more than 288 samples are stored and reported through
        the verdict.
        """
        if isinstance(download, ScanError):
            return InterfaceResult(interface=interface, cause=download.cause)

        parsed_log = self._parser.parse(download)
        samples = self._day_filter.apply(parsed_log.samples)
        verdict = self._validator.evaluate(len(samples))
        invalid_line_count = len(parsed_log.invalid_line_numbers)
        if verdict is SampleCountVerdict.EMPTY:
            return InterfaceResult(
                interface=interface,
                cause=FailureCause.NO_VALID_SAMPLES,
                invalid_line_count=invalid_line_count,
            )

        daily_traffic = DailyTraffic(
            interface_id=interface.interface_id,
            layer=layer,
            date=self._target_date.key,
            samples=samples,
        )
        try:
            self._store(daily_traffic)
        except DatabaseError:
            return InterfaceResult(
                interface=interface,
                cause=FailureCause.STORAGE_ERROR,
                sample_count=len(samples),
                verdict=verdict,
                invalid_line_count=invalid_line_count,
            )
        return InterfaceResult(
            interface=interface,
            sample_count=len(samples),
            verdict=verdict,
            invalid_line_count=invalid_line_count,
        )

    def _store(self, daily_traffic: DailyTraffic) -> None:
        """Store the day; with `force`, delete the summary and the raw day first [RF-021]."""
        if self._force:
            self._summary_store.delete_day(daily_traffic.interface_id, daily_traffic.date)
            self._traffic_store.delete_day(daily_traffic.interface_id, daily_traffic.date)
        self._traffic_store.save(daily_traffic)
