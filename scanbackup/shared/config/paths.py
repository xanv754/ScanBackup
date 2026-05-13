import shutil
from os import path
from pathlib import Path
from scanbackup.shared.config.metadata import FOLDER_INFO, FOLDER_LOGS


class PathConfig:
    """All paths of the system."""

    FOLDER_ROOT = Path(
        path.abspath(path.join(path.dirname(__file__), "..", "..", ".."))
    )
    FOLDER_LOG = Path(path.join(FOLDER_ROOT, FOLDER_INFO, FOLDER_LOGS))
    FOLDER_TMP = Path(path.join(FOLDER_ROOT, FOLDER_INFO, "tmp"))

    @staticmethod
    def create_folder(path: Path, empty: bool = False) -> None:
        path = path.parent
        path.mkdir(parents=True, exist_ok=True)
        if empty:
            for content in path.iterdir():
                if content.is_file():
                    content.unlink()
                elif content.is_dir():
                    shutil.rmtree(content)
