from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from reports.constants.constants import TEMPORARY_FILE_SUFFIX
from reports.exceptions import ExportError


class AtomicFileWriter:
    """Writes a file through a temporary file of the same directory and `os.replace`.

    The temporary file is in the same directory so the replace is atomic. It gets a unique
    name and the default permissions of the process. If anything fails it is removed.
    """

    def write(self, destination: Path, write_content: Callable[[Path], None]) -> None:
        """Call `write_content` with a temporary path, then move the result to `destination`.

        Raises `ExportError` on any failure; a previous `destination` is left untouched.
        """
        temporary_path = destination.with_name(
            f".{destination.name}.{uuid4().hex}{TEMPORARY_FILE_SUFFIX}"
        )
        try:
            write_content(temporary_path)
            temporary_path.replace(destination)
        except Exception as error:
            temporary_path.unlink(missing_ok=True)
            raise ExportError(f"{type(error).__name__}: {error}") from error
