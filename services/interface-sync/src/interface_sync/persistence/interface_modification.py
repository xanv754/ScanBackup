from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from interface_sync.constants.enums import InterfaceStatus
from interface_sync.persistence.interface_document import InterfaceDocument


class InterfaceModification(BaseModel):
    """The change of one stored interface, applied as a single update with one `updated_at`.

    `field_changes` maps each modified data field to its `(previous, new)` values.
    `status_change` is the `(previous, new)` status, or `None` when the status is kept.
    """

    model_config = ConfigDict(frozen=True)

    scan_url: str
    updated_at: datetime
    field_changes: dict[str, tuple[str | float, str | float]] = Field(default_factory=dict)
    status_change: tuple[InterfaceStatus, InterfaceStatus] | None = None

    @property
    def changes_data(self) -> bool:
        """Return `True` when at least one data field (not the status) changes."""
        return bool(self.field_changes)

    @property
    def is_decommission(self) -> bool:
        """Return `True` when the interface becomes `desincorporada`."""
        return self.status_change is not None and (
            self.status_change[1] is InterfaceStatus.DECOMMISSIONED
        )

    @property
    def is_reactivation(self) -> bool:
        """Return `True` when the interface becomes `activa` again."""
        return self.status_change is not None and self.status_change[1] is InterfaceStatus.ACTIVE


class InterfaceChanges(BaseModel):
    """The set of writes the repository applies in one ordered bulk operation.

    `unchanged_count` only feeds the summaries; it is never written.
    """

    model_config = ConfigDict(frozen=True)

    registrations: list[InterfaceDocument] = Field(default_factory=list)
    modifications: list[InterfaceModification] = Field(default_factory=list)
    unchanged_count: int = 0

    @property
    def updated_count(self) -> int:
        """Return how many modifications change data fields."""
        return sum(1 for modification in self.modifications if modification.changes_data)

    @property
    def decommissioned_count(self) -> int:
        """Return how many modifications decommission an interface."""
        return sum(1 for modification in self.modifications if modification.is_decommission)

    @property
    def reactivated_count(self) -> int:
        """Return how many modifications reactivate an interface."""
        return sum(1 for modification in self.modifications if modification.is_reactivation)
