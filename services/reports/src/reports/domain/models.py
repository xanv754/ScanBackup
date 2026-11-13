from dataclasses import dataclass

from bson import ObjectId


@dataclass(frozen=True, slots=True)
class InterfaceInfo:
    """Descriptive data of an interface, always read from `interfaces` [RF-034]."""

    id: ObjectId
    name: str
    vendor: str
    capacity_gbps: float
    scan_url: str


@dataclass(frozen=True, slots=True)
class AggregatedSummary:
    """Daily summaries of an interface in the range, aggregated by the database in bps."""

    interface_id: ObjectId
    in_average_bps: float
    out_average_bps: float
    in_max_bps: float
    out_max_bps: float
    days: int


@dataclass(frozen=True, slots=True)
class InterfaceRow:
    """The values of an interface in the report, already in Gbps [RF-035 to RF-038].

    `scan_url` is not exported: it only breaks ties so the row order is deterministic.
    """

    name: str
    in_average_gbps: float
    in_max_gbps: float
    out_average_gbps: float
    out_max_gbps: float
    capacity_gbps: float
    vendor: str
    usage_percent: float
    scan_url: str

    @property
    def sort_key(self) -> tuple[str, str, str]:
        """Return the ordering key: type, interface name and, to break ties, the SCAN URL."""
        return (self.vendor, self.name, self.scan_url)


@dataclass(frozen=True, slots=True)
class LayerData:
    """The rows of a layer, sorted as they are written in its sheet [RF-040]."""

    layer: str
    rows: tuple[InterfaceRow, ...]
