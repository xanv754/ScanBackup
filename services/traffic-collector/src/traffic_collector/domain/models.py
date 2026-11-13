from dataclasses import dataclass
from datetime import datetime

from bson import ObjectId


@dataclass(frozen=True, slots=True)
class ActiveInterface:
    """An active interface and the SCAN URL where its traffic log is queried."""

    interface_id: ObjectId
    scan_url: str


@dataclass(frozen=True, slots=True)
class Sample:
    """One 5-minute traffic sample. `ts` is UTC; values are raw SCAN values (probably bytes/s)."""

    ts: datetime
    in_avg: float
    out_avg: float
    in_max: float
    out_max: float


@dataclass(frozen=True, slots=True)
class DailyTraffic:
    """The samples of one interface for one day (bucket of `traffic_daily`)."""

    interface_id: ObjectId
    layer: str
    date: str
    samples: tuple[Sample, ...]


@dataclass(frozen=True, slots=True)
class DailySummary:
    """The summary of one interface for one day (document of `traffic_summary_daily`).

    The values are the raw SCAN values times 8.022 (bps if SCAN reports bytes/s).
    The usage percentage is not stored; reports calculate it.
    """

    interface_id: ObjectId
    date: str
    in_avg: float
    out_avg: float
    in_max: float
    out_max: float
