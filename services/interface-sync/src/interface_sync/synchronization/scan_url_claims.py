from interface_sync.models import ValidatedListing


class ScanUrlClaims:
    """Remembers, during one run, which `scan_url` was already taken by a page.

    SCAN may show the same interface in two pages. Since `scan_url` is the identity, only the
    first page processed (the order of `config.yml`) keeps it; later pages drop it from their
    listing so the interface is not rewritten with another layer on every run [RF-011].
    """

    def __init__(self) -> None:
        """Start with no `scan_url` taken."""
        self._claimed_scan_urls: set[str] = set()

    def claim(self, listing: ValidatedListing) -> tuple[ValidatedListing, list[str]]:
        """Return the listing without the already taken interfaces and those duplicated `scan_url`.

        `present_scan_urls` is kept intact: a duplicated interface is still shown by the page.
        """
        remaining = []
        duplicated_scan_urls = []
        for interface in listing.complete_interfaces:
            scan_url = str(interface.scan_url)
            if scan_url in self._claimed_scan_urls:
                duplicated_scan_urls.append(scan_url)
                continue
            self._claimed_scan_urls.add(scan_url)
            remaining.append(interface)
        return listing.model_copy(update={"complete_interfaces": remaining}), duplicated_scan_urls
