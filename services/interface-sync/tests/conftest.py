from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from interface_sync.constants.enums import InterfaceStatus
from interface_sync.models import ScrapedInterface, ValidatedListing
from interface_sync.persistence import InterfaceDocument
from interface_sync.utils.logger import ServiceLogger


class RecordingLogger(ServiceLogger):
    """Logger double that keeps `(level, message, details)` tuples instead of writing a file."""

    def __init__(self) -> None:
        self.records: list[tuple[str, str, str]] = []

    def info(self, message: str, details: str = "") -> None:
        self.records.append(("info", message, details))

    def warning(self, message: str, details: str = "") -> None:
        self.records.append(("warning", message, details))

    def error(self, message: str, details: str = "") -> None:
        self.records.append(("error", message, details))

    def messages(self, level: str) -> list[str]:
        return [message for record_level, message, _ in self.records if record_level == level]


@pytest.fixture
def recording_logger() -> RecordingLogger:
    return RecordingLogger()


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 3, 10, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def earlier() -> datetime:
    return datetime(2026, 1, 1, 8, 30, 0, tzinfo=UTC)


@pytest.fixture
def make_scraped() -> Callable[..., ScrapedInterface]:
    def factory(**overrides: object) -> ScrapedInterface:
        values: dict[str, object] = {
            "position": 1,
            "name": "IF-1",
            "scan_url": "http://scan/1.log",
            "capacity_gbps": 10.0,
            "vendor": "HUAWEI",
            "layer": "BORDE",
        }
        values.update(overrides)
        return ScrapedInterface(**values)

    return factory


@pytest.fixture
def make_listing() -> Callable[..., ValidatedListing]:
    def factory(
        interfaces: list[ScrapedInterface],
        present_scan_urls: set[str] | None = None,
    ) -> ValidatedListing:
        present = (
            present_scan_urls
            if present_scan_urls is not None
            else {interface.scan_url for interface in interfaces if interface.scan_url}
        )
        return ValidatedListing(
            complete_interfaces=interfaces,
            present_scan_urls=frozenset(present),
            incomplete_count=0,
            defaulted_capacity_count=0,
        )

    return factory


@pytest.fixture
def make_document(earlier: datetime) -> Callable[..., InterfaceDocument]:
    def factory(**overrides: object) -> InterfaceDocument:
        values: dict[str, object] = {
            "layer": "BORDE",
            "name": "IF-1",
            "vendor": "HUAWEI",
            "capacity_gbps": 10.0,
            "scan_url": "http://scan/1.log",
            "status": InterfaceStatus.ACTIVE,
            "created_at": earlier,
            "updated_at": earlier,
        }
        values.update(overrides)
        return InterfaceDocument(**values)

    return factory
