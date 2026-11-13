from typing import Any

import pytest

from interface_sync.constants.enums import LogEvent
from interface_sync.exceptions import (
    PageFetchError,
    ScanConnectionError,
    ScanHttpError,
    ScanTimeoutError,
    ScanUnauthorizedError,
)
from interface_sync.models import PageConfig
from interface_sync.scraping import ScanAvailabilityChecker


class FakeProber:
    def __init__(self, failures: dict[str, PageFetchError] | None = None) -> None:
        self._failures = failures or {}
        self.probed: list[str] = []

    def probe(self, url: str) -> None:
        self.probed.append(url)
        if url in self._failures:
            raise self._failures[url]


def page(url: str, layer: str = "borde") -> PageConfig:
    return PageConfig(layer=layer, url=url)


def test_each_distinct_base_url_is_probed_once(recording_logger: Any) -> None:
    """Startup: pages sharing scheme and host produce a single request."""
    prober = FakeProber()
    checker = ScanAvailabilityChecker(prober, recording_logger)

    checks = checker.check(
        [
            page("https://scan-a.example/cgi/one.cgi?x"),
            page("https://scan-a.example/cgi/two.cgi", "dist"),
            page("https://scan-b.example:8443/cgi/three.cgi", "rai"),
        ]
    )

    assert prober.probed == ["https://scan-a.example", "https://scan-b.example:8443"]
    assert all(check.responded for check in checks)


def test_success_is_logged_as_info(recording_logger: Any) -> None:
    """Startup: an answering base URL is registered in the log."""
    ScanAvailabilityChecker(FakeProber(), recording_logger).check([page("http://scan/a")])

    assert recording_logger.records == [("info", LogEvent.SCAN_BASE_RESPONDED, "http://scan")]


@pytest.mark.parametrize(
    "error",
    [ScanTimeoutError(), ScanConnectionError(), ScanUnauthorizedError(), ScanHttpError(503)],
)
def test_failure_is_logged_as_error_with_cause(
    recording_logger: Any, error: PageFetchError
) -> None:
    """Startup: a base URL that does not answer is registered with its cause."""
    prober = FakeProber({"http://scan": error})

    checks = ScanAvailabilityChecker(prober, recording_logger).check([page("http://scan/a")])

    assert not checks[0].responded
    assert checks[0].cause == error.cause
    assert recording_logger.records == [
        ("error", LogEvent.SCAN_BASE_UNREACHABLE, f"http://scan ({error.cause})")
    ]


def test_every_base_url_is_checked_after_a_failure(recording_logger: Any) -> None:
    """Startup: a failure does not hide the state of the remaining base URLs."""
    prober = FakeProber({"http://scan-a": ScanConnectionError()})

    checks = ScanAvailabilityChecker(prober, recording_logger).check(
        [page("http://scan-a/x"), page("http://scan-b/y", "dist")]
    )

    assert [check.responded for check in checks] == [False, True]


def test_base_url_drops_credentials_and_lowercases_scheme() -> None:
    """Startup: credentials in the URL never reach the log."""
    assert page("HTTPS://user:pass@scan.example:8443/a").base_url == "https://scan.example:8443"
