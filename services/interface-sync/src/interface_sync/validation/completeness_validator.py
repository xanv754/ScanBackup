from pydantic import BaseModel, ConfigDict

from interface_sync.models import ScrapedInterface


class IncompleteInterface(BaseModel):
    """An interface that lacks required data, with the names of the missing fields."""

    model_config = ConfigDict(frozen=True)

    interface: ScrapedInterface
    missing_fields: list[str]


class CompletenessResult(BaseModel):
    """The interfaces of a listing split into complete and incomplete ones."""

    model_config = ConfigDict(frozen=True)

    complete: list[ScrapedInterface]
    incomplete: list[IncompleteInterface]


class CompletenessValidator:
    """Detects interfaces without `name` or `scan_url` [RF-004]. It is pure: no logs, no I/O."""

    REQUIRED_FIELDS = ("name", "scan_url")

    def split(self, interfaces: list[ScrapedInterface]) -> CompletenessResult:
        """Separate complete interfaces from incomplete ones, keeping the listing order.

        A required field is missing when it is `None`, empty or only whitespace.
        """
        complete: list[ScrapedInterface] = []
        incomplete: list[IncompleteInterface] = []

        for interface in interfaces:
            missing_fields = self._find_missing_fields(interface)
            if missing_fields:
                incomplete.append(
                    IncompleteInterface(interface=interface, missing_fields=missing_fields)
                )
            else:
                complete.append(interface)

        return CompletenessResult(complete=complete, incomplete=incomplete)

    def _find_missing_fields(self, interface: ScrapedInterface) -> list[str]:
        """Return the names of the required fields that have no usable value."""
        return [
            field_name
            for field_name in self.REQUIRED_FIELDS
            if not (getattr(interface, field_name) or "").strip()
        ]
