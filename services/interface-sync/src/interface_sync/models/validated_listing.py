from pydantic import BaseModel, ConfigDict

from interface_sync.models.scraped_interface import ScrapedInterface


class ValidatedListing(BaseModel):
    """The outcome of validating a page listing that is valid.

    `complete_interfaces` are the interfaces that continue the process, with their capacity
    already normalized. `present_scan_urls` holds the `scan_url` of every interface shown by
    the page that has one, including the incomplete ones, so they are never decommissioned.
    The counters feed the page summary.
    """

    model_config = ConfigDict(frozen=True)

    complete_interfaces: list[ScrapedInterface]
    present_scan_urls: frozenset[str]
    incomplete_count: int
    defaulted_capacity_count: int
