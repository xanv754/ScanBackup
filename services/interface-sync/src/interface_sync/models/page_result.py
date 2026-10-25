from pydantic import BaseModel, ConfigDict


class PageResult(BaseModel):
    """The outcome of processing one configured page, with scraping and database kept apart.

    `cause` is why the scraping or validation failed; `database_cause` is why the storage
    failed. The page succeeded only when both are `None`. `present_scan_urls` holds every
    `scan_url` shown by a successful page, which the layer decommission needs.
    """

    model_config = ConfigDict(frozen=True)

    page_label: str
    layer: str
    cause: str | None = None
    database_cause: str | None = None
    present_scan_urls: frozenset[str] = frozenset()

    @property
    def scraping_succeeded(self) -> bool:
        """Return `True` when the page was scraped and validated without failure."""
        return self.cause is None

    @property
    def database_succeeded(self) -> bool:
        """Return `True` when the page storage did not fail."""
        return self.database_cause is None

    @property
    def succeeded(self) -> bool:
        """Return `True` when neither the scraping nor the database failed."""
        return self.scraping_succeeded and self.database_succeeded
