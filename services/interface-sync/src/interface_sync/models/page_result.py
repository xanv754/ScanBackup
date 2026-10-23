from pydantic import BaseModel, ConfigDict


class PageResult(BaseModel):
    """The outcome of processing one configured page; a `cause` means the page failed."""

    model_config = ConfigDict(frozen=True)

    page_label: str
    cause: str | None = None

    @property
    def succeeded(self) -> bool:
        """Return `True` when the page was processed without failure."""
        return self.cause is None
