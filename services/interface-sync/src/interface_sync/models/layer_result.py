from pydantic import BaseModel, ConfigDict


class LayerResult(BaseModel):
    """The outcome of decommissioning the missing interfaces of one layer.

    `skipped_reason` is set when the layer was not evaluated because one of its pages failed.
    `database_cause` is set when the database failed while decommissioning.
    """

    model_config = ConfigDict(frozen=True)

    layer: str
    decommissioned_count: int = 0
    skipped_reason: str | None = None
    database_cause: str | None = None

    @property
    def succeeded(self) -> bool:
        """Return `True` when the database did not fail for this layer."""
        return self.database_cause is None
