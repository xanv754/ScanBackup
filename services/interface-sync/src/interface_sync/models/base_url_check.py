from pydantic import BaseModel, ConfigDict


class BaseUrlCheck(BaseModel):
    """The outcome of checking one SCAN base URL; `cause` is why it did not answer."""

    model_config = ConfigDict(frozen=True)

    base_url: str
    cause: str | None = None

    @property
    def responded(self) -> bool:
        """Return `True` when the base URL answered."""
        return self.cause is None
