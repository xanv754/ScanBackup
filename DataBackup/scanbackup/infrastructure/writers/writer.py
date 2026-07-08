from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel


class BaseWriter(ABC):
    dir: Path

    def __init__(self, dir: Path | None = None) -> None:
        if not dir:
            self.dir = Path(self._get_home())
        else:
            self.dir = dir

    def _get_home(self) -> str:
        home = Path.home()
        donwload_dir = home / "Downloads"
        if donwload_dir.exists():
            return str(donwload_dir.resolve())
        donwload_dir = home / "Descargas"
        if donwload_dir.exists():
            return str(donwload_dir.resolve())
        return str(home.resolve())

    @abstractmethod
    def export(self, filename: str, data: list[BaseModel]) -> None:
        pass
