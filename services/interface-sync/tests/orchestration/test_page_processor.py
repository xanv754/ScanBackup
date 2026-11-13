from collections.abc import Callable
from typing import Any

import pytest

from interface_sync.constants.enums import LogEvent
from interface_sync.exceptions import DatabaseError, PageFetchError, ScanConnectionError
from interface_sync.models import PageConfig, ScrapedInterface
from interface_sync.orchestration import PageProcessor
from interface_sync.persistence import InterfaceChanges, InterfaceDocument
from interface_sync.synchronization import ChangeReporter, InterfaceChangePlanner, ScanUrlClaims
from interface_sync.utils.logger import ServiceLogger
from interface_sync.validation import CapacityValidator, CompletenessValidator, ListingValidator

Scraped = Callable[..., ScrapedInterface]
Document = Callable[..., InterfaceDocument]


class FakeScraper:
    def __init__(self, interfaces: list[ScrapedInterface] | PageFetchError) -> None:
        self._interfaces = interfaces

    def scrape(self, page: PageConfig) -> list[ScrapedInterface]:
        if isinstance(self._interfaces, PageFetchError):
            raise self._interfaces
        return self._interfaces


class FakeRepository:
    def __init__(self, stored: list[InterfaceDocument] | None = None) -> None:
        self.stored = stored or []
        self.applied: list[InterfaceChanges] = []
        self.find_calls = 0
        self.fail_on_find = False
        self.fail_on_apply = False

    def find_by_scan_urls(self, scan_urls: set[str]) -> list[InterfaceDocument]:
        self.find_calls += 1
        if self.fail_on_find:
            raise DatabaseError()
        return [document for document in self.stored if document.scan_url in scan_urls]

    def apply(self, changes: InterfaceChanges) -> None:
        if self.fail_on_apply:
            raise DatabaseError()
        self.applied.append(changes)


def build_processor(
    interfaces: list[ScrapedInterface] | PageFetchError,
    repository: FakeRepository,
    logger: ServiceLogger,
    claims: ScanUrlClaims | None = None,
) -> PageProcessor:
    return PageProcessor(
        FakeScraper(interfaces),  # type: ignore[arg-type]
        ListingValidator(CompletenessValidator(), CapacityValidator(), logger),
        repository,  # type: ignore[arg-type]
        InterfaceChangePlanner(),
        ChangeReporter(logger),
        claims or ScanUrlClaims(),
        logger,
    )


@pytest.fixture
def page() -> PageConfig:
    return PageConfig(layer="borde", url="http://scan/borde", vendor="huawei")


def test_successful_page_registers_new_interfaces(
    page: PageConfig, make_scraped: Scraped, recording_logger: Any
):
    """RF-007: a new interface of a valid page is written and the page succeeds."""
    repository = FakeRepository()
    processor = build_processor([make_scraped()], repository, recording_logger)

    result = processor.process(page)

    assert result.succeeded
    assert result.layer == "BORDE"
    assert result.present_scan_urls == frozenset({"http://scan/1.log"})
    [changes] = repository.applied
    assert [document.scan_url for document in changes.registrations] == ["http://scan/1.log"]
    assert LogEvent.PAGE_SUMMARY in recording_logger.messages("info")
    assert LogEvent.PAGE_SUCCEEDED in recording_logger.messages("info")


def test_page_summary_reports_every_counter(
    page: PageConfig, make_scraped: Scraped, make_document: Document, recording_logger: Any
):
    """RF-014: the page summary lists new, updated, reactivated, unchanged and incomplete."""
    interfaces = [
        make_scraped(position=1, scan_url="http://scan/new.log"),
        make_scraped(position=2, scan_url="http://scan/changed.log", name="NEW"),
        make_scraped(position=3, scan_url="http://scan/same.log"),
        make_scraped(position=4, scan_url=None),
    ]
    stored = [
        make_document(scan_url="http://scan/changed.log", name="OLD"),
        make_document(scan_url="http://scan/same.log"),
    ]
    processor = build_processor(interfaces, FakeRepository(stored), recording_logger)

    processor.process(page)

    [(_, _, details)] = [
        record for record in recording_logger.records if record[1] == LogEvent.PAGE_SUMMARY
    ]
    assert details == (
        "BORDE HUAWEI | nuevas: 1 | actualizadas: 1 | reactivadas: 0 | sin cambios: 1 | "
        "incompletas: 1 | duplicadas: 0 | capacidad por defecto: 0"
    )


def test_incomplete_interface_is_present_but_never_stored(
    page: PageConfig, make_scraped: Scraped, recording_logger: Any
):
    """RF-004/RF-009: an incomplete interface is not stored but its scan_url counts as present."""
    interfaces = [
        make_scraped(position=1),
        make_scraped(position=2, name=None, scan_url="http://scan/2.log"),
    ]
    repository = FakeRepository()
    processor = build_processor(interfaces, repository, recording_logger)

    result = processor.process(page)

    assert result.present_scan_urls == frozenset({"http://scan/1.log", "http://scan/2.log"})
    assert [document.scan_url for document in repository.applied[0].registrations] == [
        "http://scan/1.log"
    ]


def test_scraping_failure_never_touches_the_database(page: PageConfig, recording_logger: Any):
    """RF-010: a page that could not be scraped does not read or write anything."""
    repository = FakeRepository()
    processor = build_processor(ScanConnectionError(), repository, recording_logger)

    result = processor.process(page)

    assert not result.succeeded
    assert result.cause == "sin conexión a SCAN"
    assert result.database_cause is None
    assert result.layer == "BORDE"
    assert result.present_scan_urls == frozenset()
    assert repository.find_calls == 0
    assert repository.applied == []
    assert recording_logger.messages("error") == [LogEvent.PAGE_FAILED]


def test_empty_listing_never_reaches_the_database(page: PageConfig, recording_logger: Any):
    """RF-006: an empty listing is an invalid page and is kept out of the storage."""
    repository = FakeRepository()
    processor = build_processor([], repository, recording_logger)

    result = processor.process(page)

    assert not result.scraping_succeeded
    assert "listado inválido" in str(result.cause)
    assert repository.find_calls == 0
    assert repository.applied == []


def test_listing_with_only_incomplete_interfaces_never_reaches_the_database(
    page: PageConfig, make_scraped: Scraped, recording_logger: Any
):
    """RF-006: when every interface is incomplete the page is invalid and nothing is stored."""
    interfaces = [make_scraped(name=None), make_scraped(scan_url=None)]
    repository = FakeRepository()
    processor = build_processor(interfaces, repository, recording_logger)

    result = processor.process(page)

    assert not result.scraping_succeeded
    assert repository.find_calls == 0


@pytest.mark.parametrize("failing_step", ["fail_on_find", "fail_on_apply"])
def test_database_failure_is_reported_apart_from_a_successful_scraping(
    page: PageConfig, make_scraped: Scraped, recording_logger: Any, failing_step: str
):
    """RF-010: a database error fails the page but the scraping result stays successful."""
    repository = FakeRepository()
    setattr(repository, failing_step, True)
    processor = build_processor([make_scraped()], repository, recording_logger)

    result = processor.process(page)

    assert not result.succeeded
    assert result.scraping_succeeded
    assert result.cause is None
    assert result.database_cause == "error de base de datos"
    assert result.present_scan_urls == frozenset()
    assert recording_logger.messages("error") == [LogEvent.DATABASE_FAILED]
    assert LogEvent.PAGE_SUCCEEDED not in recording_logger.messages("info")
    assert LogEvent.PAGE_SUMMARY not in recording_logger.messages("info")


def test_changes_are_logged_only_after_a_successful_write(
    page: PageConfig, make_scraped: Scraped, make_document: Document, recording_logger: Any
):
    """RF-014: a failed write must not leave logs claiming the changes were applied."""
    repository = FakeRepository([make_document(name="OLD")])
    repository.fail_on_apply = True
    processor = build_processor([make_scraped(name="NEW")], repository, recording_logger)

    processor.process(page)

    assert LogEvent.INTERFACE_UPDATED not in recording_logger.messages("info")


def test_updated_interface_is_logged_after_a_successful_write(
    page: PageConfig, make_scraped: Scraped, make_document: Document, recording_logger: Any
):
    """RF-014: an applied update is logged with its scan_url and values."""
    repository = FakeRepository([make_document(name="OLD")])
    processor = build_processor([make_scraped(name="NEW")], repository, recording_logger)

    processor.process(page)

    assert ("info", LogEvent.INTERFACE_UPDATED, "http://scan/1.log | name: OLD -> NEW") in (
        recording_logger.records
    )


def test_page_queries_the_database_once_for_all_its_interfaces(
    page: PageConfig, make_scraped: Scraped, recording_logger: Any
):
    """Efficiency: one query per page, never one per interface."""
    interfaces = [
        make_scraped(position=position, scan_url=f"http://scan/{position}.log")
        for position in range(1, 6)
    ]
    repository = FakeRepository()
    processor = build_processor(interfaces, repository, recording_logger)

    processor.process(page)

    assert repository.find_calls == 1
    assert len(repository.applied) == 1


def test_scan_url_shown_by_two_pages_is_stored_only_by_the_first(
    make_scraped: Scraped, recording_logger: Any
):
    """RF-011: the second page drops the shared scan_url, warns, and still counts it present."""
    repository = FakeRepository()
    claims = ScanUrlClaims()
    dist_page = PageConfig(layer="dist", url="http://scan/dist", vendor="huawei")
    rai_page = PageConfig(layer="rai", url="http://scan/rai", vendor="huawei")
    shared = "http://scan/shared.log"

    build_processor(
        [make_scraped(scan_url=shared, layer="DIST")], repository, recording_logger, claims
    ).process(dist_page)
    second = build_processor(
        [make_scraped(scan_url=shared, layer="RAI")], repository, recording_logger, claims
    ).process(rai_page)

    assert [len(changes.registrations) for changes in repository.applied] == [1, 0]
    assert repository.applied[0].registrations[0].layer == "DIST"
    assert second.succeeded
    assert second.present_scan_urls == frozenset({shared})
    assert ("warning", LogEvent.DUPLICATED_INTERFACE, f"RAI HUAWEI | {shared}") in (
        recording_logger.records
    )
