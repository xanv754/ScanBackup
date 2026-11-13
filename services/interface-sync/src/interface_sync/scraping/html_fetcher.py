from typing import Protocol


class HtmlFetcher(Protocol):
    """Anything that can download the HTML of a SCAN page."""

    def fetch_html(self, url: str) -> str:  # type: ignore
        """Return the HTML text of the page at `url`; raise `PageFetchError` on failure."""
