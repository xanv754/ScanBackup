from abc import ABC, abstractmethod

from interface_sync.models import ScrapedInterface


class PageParser(ABC):
    """Extracts the interfaces from the HTML of one SCAN listing page (one layer and vendor)."""

    @abstractmethod
    def parse(self, html: str, page_url: str) -> list[ScrapedInterface]:
        """Return every interface shown in the listing, in page order.

        Summary blocks ("Sumatoria") are never returned. An empty list means the page
        structure exists but has no rows. Raise `UnreadablePageError` if the structure is absent.
        """
