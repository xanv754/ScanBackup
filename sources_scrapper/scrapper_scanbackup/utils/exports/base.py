from pydantic import BaseModel
from scrapper_scanbackup.utils import ScrapperSetting
from abc import abstractmethod
from pathlib import Path


class Exporter:
    layer: str
    filepath: Path
    delimiter: str

    def __init__(
        self, layer: str, setting: ScrapperSetting, outdir: Path | None = None
    ) -> None:
        self.layer = layer
        export_setting = setting.get_exporter()
        if not outdir:
            self.filepath = export_setting.dir / f"{layer.upper().strip()}"
        else:
            self.filepath = outdir / f"{layer.upper().strip()}"
        self.delimiter = export_setting.delimiter

    @abstractmethod
    def export(self, data: list[BaseModel]) -> None:
        pass
