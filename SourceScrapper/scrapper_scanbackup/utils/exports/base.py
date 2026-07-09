from typing import TypeVar
from pydantic import BaseModel
from scrapper_scanbackup.utils import ScrapperSetting
from abc import abstractmethod
from pathlib import Path

Model = TypeVar("Model", bound=BaseModel)


class Exporter:
    layer: str
    filepath: Path
    delimiter: str
    header_text: str

    def __init__(
        self,
        layer: str,
        setting: ScrapperSetting,
        outdir: Path | None = None,
        ip: bool = False,
    ) -> None:
        self.layer = layer
        export_setting = setting.get_exporter()
        if not outdir:
            self.filepath = export_setting.dir / f"{layer.upper().strip()}"
        else:
            self.filepath = outdir / f"{layer.upper().strip()}"
        header_setting = setting.get_header()
        self.delimiter = export_setting.delimiter
        if not ip:
            self.header_text = (
                header_setting.link
                + self.delimiter
                + header_setting.interface
                + self.delimiter
                + header_setting.capacity
                + self.delimiter
                + header_setting.type
            )
        else:
            self.header_text = (
                header_setting.link + self.delimiter + header_setting.interface
            )

    @abstractmethod
    def export(self, data: list[Model]) -> None:
        pass
