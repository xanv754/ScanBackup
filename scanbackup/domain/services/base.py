from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict
from os import path
from datetime import datetime
from pandas import DataFrame
from scanbackup.shared.config.metadata import PREFFIX_FILE_EXPORT


class BaseExport(ABC):
    _content: Dict[str, DataFrame]
    _filepath: Path

    def __init__(self, data: Dict[str, DataFrame], filename: str | None = None) -> None:
        self._content = data
        self._generate_filepath(filename)

    def _generate_filepath(self, filename: str | None = None) -> None:
        """Generate filepath to export data."""
        home = Path.home()
        if not filename:
            file = (
                f"{PREFFIX_FILE_EXPORT}_{datetime.now().strftime("%Y-%m-%d_$H:$M:$S")}"
            )
        else:
            file = f"{PREFFIX_FILE_EXPORT}_{filename}_{datetime.now().strftime("%Y-%m-%d_$H:$M:$S")}"
        if Path(home / "Downloads").exists():
            self._filepath = Path(path.join(home, "Downloads", file))
        elif Path(home / "Descargas").exists():
            self._filepath = Path(path.join(home, "Descargas", file))
        else:
            self._filepath = Path(path.join(home, file))

    def get_filepath(self) -> str:
        return self._filepath.resolve()

    def get_data(self) -> Dict[str, DataFrame]:
        return self._content

    @abstractmethod
    def execute(self) -> bool:
        pass
