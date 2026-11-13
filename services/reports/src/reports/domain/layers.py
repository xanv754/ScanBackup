from collections.abc import Iterable
from dataclasses import dataclass

FIXED_LAYERS = ("BORDE", "BRAS", "CACHING", "RAI", "DINT", "DIST", "IXP")


def canonical_layer_name(stored_value: str) -> str:
    """Return the canonical name of a layer: trimmed and in uppercase [RF-034]."""
    return stored_value.strip().upper()


@dataclass(frozen=True, slots=True)
class Layer:
    """A layer of the report: its canonical name and the values stored in `interfaces`."""

    name: str
    stored_values: tuple[str, ...]


class LayerCatalog:
    """The existing layers, grouped by canonical name and sorted in report order [RF-039].

    `FIXED_LAYERS` is the only place that knows the fixed layers and their order. It is not an
    enumeration on purpose: any other layer found in the database is included without changing
    the code. A fixed layer without interfaces is not an existing layer.
    """

    def __init__(self, stored_layer_values: Iterable[str]) -> None:
        """Group the distinct stored values by canonical name."""
        stored_by_name: dict[str, set[str]] = {}
        for stored_value in stored_layer_values:
            stored_by_name.setdefault(canonical_layer_name(stored_value), set()).add(
                stored_value
            )
        self._stored_by_name = stored_by_name

    def ordered(self) -> tuple[Layer, ...]:
        """Return the existing fixed layers in their order, then the others alphabetically."""
        fixed_names = [name for name in FIXED_LAYERS if name in self._stored_by_name]
        other_names = sorted(
            name for name in self._stored_by_name if name not in FIXED_LAYERS
        )
        return tuple(
            Layer(name=name, stored_values=tuple(sorted(self._stored_by_name[name])))
            for name in (*fixed_names, *other_names)
        )
