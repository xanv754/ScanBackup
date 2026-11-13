from abc import ABC, abstractmethod
from pathlib import Path

from reports.domain.models import LayerData


class ReportExporter(ABC):
    """Writes the report in a file format. A new format is a new implementation of this class.

    The exporter receives the data layer by layer, so it can release each layer before the next
    one is read. It knows nothing about the database or how the values were calculated.
    """

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Return the extension of the files it writes, with the dot (for example `.xlsx`)."""

    @abstractmethod
    def validate_layer_name(self, layer_name: str) -> None:
        """Raise `InvalidSheetNameError` if the canonical layer name cannot name a sheet.

        It is called before the data of the layer is read [RF-043].
        """

    @abstractmethod
    def add_layer(self, data: LayerData) -> None:
        """Add a sheet with the rows of a layer. Layers are added in report order [RF-039]."""

    @abstractmethod
    def save(self, destination: Path) -> None:
        """Write the file atomically at `destination`, replacing a previous file [RF-042].

        Raises `ExportError` if there is no sheet or the file cannot be written. On failure no
        partial file is left and a previous file with the same name stays intact.
        """
