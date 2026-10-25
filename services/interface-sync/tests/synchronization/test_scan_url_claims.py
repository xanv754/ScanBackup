from collections.abc import Callable

from interface_sync.models import ScrapedInterface, ValidatedListing
from interface_sync.synchronization import ScanUrlClaims

Scraped = Callable[..., ScrapedInterface]
Listing = Callable[..., ValidatedListing]


def test_first_page_keeps_all_its_interfaces(make_scraped: Scraped, make_listing: Listing):
    """RF-011: nothing is dropped from the first page that shows a scan_url."""
    claims = ScanUrlClaims()
    listing = make_listing([make_scraped(scan_url="http://scan/a.log")])

    claimed_listing, duplicated = claims.claim(listing)

    assert claimed_listing.complete_interfaces == listing.complete_interfaces
    assert duplicated == []


def test_later_page_drops_scan_urls_taken_by_an_earlier_page(
    make_scraped: Scraped, make_listing: Listing
):
    """RF-011: the first page in config.yml order owns a scan_url shown by two pages."""
    claims = ScanUrlClaims()
    claims.claim(make_listing([make_scraped(scan_url="http://scan/shared.log", layer="DIST")]))
    second = make_listing(
        [
            make_scraped(position=1, scan_url="http://scan/shared.log", layer="RAI"),
            make_scraped(position=2, scan_url="http://scan/own.log", layer="RAI"),
        ]
    )

    claimed_listing, duplicated = claims.claim(second)

    assert duplicated == ["http://scan/shared.log"]
    assert [interface.scan_url for interface in claimed_listing.complete_interfaces] == [
        "http://scan/own.log"
    ]


def test_dropped_interface_still_counts_as_present(make_scraped: Scraped, make_listing: Listing):
    """RF-009: a duplicated interface stays in present_scan_urls so it is not decommissioned."""
    claims = ScanUrlClaims()
    claims.claim(make_listing([make_scraped(scan_url="http://scan/shared.log")]))
    second = make_listing([make_scraped(scan_url="http://scan/shared.log")])

    claimed_listing, _ = claims.claim(second)

    assert claimed_listing.complete_interfaces == []
    assert claimed_listing.present_scan_urls == frozenset({"http://scan/shared.log"})


def test_claiming_does_not_mutate_the_received_listing(
    make_scraped: Scraped, make_listing: Listing
):
    """The received listing is frozen data: claiming returns a copy."""
    claims = ScanUrlClaims()
    claims.claim(make_listing([make_scraped(scan_url="http://scan/shared.log")]))
    second = make_listing([make_scraped(scan_url="http://scan/shared.log")])

    claims.claim(second)

    assert len(second.complete_interfaces) == 1


def test_each_run_starts_without_claims(make_scraped: Scraped, make_listing: Listing):
    """RF-011: claims live in the instance, so a new run (new instance) starts clean."""
    listing = make_listing([make_scraped(scan_url="http://scan/a.log")])
    ScanUrlClaims().claim(listing)

    _, duplicated = ScanUrlClaims().claim(listing)

    assert duplicated == []
