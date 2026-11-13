from traffic_collector.reporting.events import Event, EventSink


class CompositeEventSink:
    """Delivers every event to several sinks, in order."""

    def __init__(self, sinks: tuple[EventSink, ...]) -> None:
        """Receive the sinks to deliver to."""
        self._sinks = sinks

    def publish(self, event: Event) -> None:
        """Deliver the event to every sink."""
        for sink in self._sinks:
            sink.publish(event)
