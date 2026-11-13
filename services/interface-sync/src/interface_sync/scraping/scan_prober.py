from typing import Protocol


class ScanProber(Protocol):
    """Anything that can check that SCAN answers at a URL."""

    def probe(self, url: str) -> None:  # type: ignore
        """Return when SCAN answers at `url`; raise `PageFetchError` otherwise."""
