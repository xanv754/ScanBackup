import shutil
from os import path
from pathlib import Path
from scanbackup.shared.config.metadata import (
    FOLDER_LOGS,
    FOLDER_INFO as FOLDER_INFO_NAME,
    LOG_FILENAME,
    LOG_EXTENSION,
)


class PathConfig:
    """All paths of the system."""

    FOLDER_ROOT = Path(
        path.abspath(path.join(path.dirname(__file__), "..", "..", ".."))
    )
    FOLDER_INFO = Path(path.join(FOLDER_ROOT, FOLDER_INFO_NAME))
    FOLDER_LOG = Path(FOLDER_INFO.resolve() / FOLDER_LOGS)
    FOLDER_TMP = Path(FOLDER_INFO.resolve() / "tmp")
    FOLDER_SOURCES = Path(FOLDER_INFO.resolve() / "sources")
    FOLDER_BBIP_DATA = Path(FOLDER_INFO.resolve() / "BBIP")
    LOG_FILE = Path(FOLDER_LOG, LOG_FILENAME).with_suffix(LOG_EXTENSION)
    SCAN_SCRIPT = Path(
        FOLDER_ROOT / "scanbackup" / "infrastructure" / "collectors" / "scan.sh"
    )

    @staticmethod
    def create_folder(target_path: Path, empty: bool = False) -> None:
        target_path.mkdir(parents=True, exist_ok=True)
        if empty:
            for content in target_path.iterdir():
                if content.is_file():
                    content.unlink()
                elif content.is_dir():
                    shutil.rmtree(content)
