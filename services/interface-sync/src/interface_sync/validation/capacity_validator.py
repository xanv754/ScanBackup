import math

from pydantic import BaseModel, ConfigDict

from interface_sync.constants.constants import FIELD_CAPACITY_GBPS
from interface_sync.models import ScrapedInterface


class CapacityResult(BaseModel):
    """Interfaces with a normalized capacity and the ones that received the default value."""

    model_config = ConfigDict(frozen=True)

    interfaces: list[ScrapedInterface]
    defaulted: list[ScrapedInterface]


class CapacityValidator:
    """Normalizes the capacity of the interfaces [RF-005]. It is pure: no logs, no I/O."""

    DEFAULT_CAPACITY_GBPS = 0.0

    def normalize(self, interfaces: list[ScrapedInterface]) -> CapacityResult:
        """Replace every invalid capacity with the default value, keeping the listing order.

        A capacity is valid when it is numeric, finite and not negative. `defaulted` holds
        the interfaces as they were received, before the replacement.
        """
        normalized: list[ScrapedInterface] = []
        defaulted: list[ScrapedInterface] = []

        for interface in interfaces:
            if self._is_valid(interface.capacity_gbps):
                normalized.append(interface)
            else:
                defaulted.append(interface)
                normalized.append(
                    interface.model_copy(update={FIELD_CAPACITY_GBPS: self.DEFAULT_CAPACITY_GBPS})
                )

        return CapacityResult(interfaces=normalized, defaulted=defaulted)

    def _is_valid(self, capacity_gbps: float | None) -> bool:
        """Tell whether the capacity is a finite, non-negative number."""
        return capacity_gbps is not None and math.isfinite(capacity_gbps) and capacity_gbps >= 0
