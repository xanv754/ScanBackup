from pathlib import Path

import pytest

from reports.exceptions import ExportError
from reports.export import AtomicFileWriter


def test_rf042_content_is_written_through_a_temporary_file_in_the_same_directory(
    tmp_path: Path,
) -> None:
    """RF-042: the content is written to a temporary path in the destination directory."""
    seen: list[Path] = []

    def write_content(path: Path) -> None:
        seen.append(path)
        path.write_text("data", encoding="utf-8")

    destination = tmp_path / "report.xlsx"
    AtomicFileWriter().write(destination, write_content)
    assert seen[0].parent == tmp_path
    assert seen[0] != destination
    assert destination.read_text(encoding="utf-8") == "data"
    assert [path.name for path in tmp_path.iterdir()] == ["report.xlsx"]


def test_rf042_failure_removes_the_temporary_file_and_keeps_the_previous_one(
    tmp_path: Path,
) -> None:
    """RF-042: a failing write leaves the previous file intact and no temporary file."""
    destination = tmp_path / "report.xlsx"
    destination.write_text("previous", encoding="utf-8")

    def write_content(path: Path) -> None:
        path.write_text("partial", encoding="utf-8")
        raise OSError("boom")

    with pytest.raises(ExportError, match="boom"):
        AtomicFileWriter().write(destination, write_content)
    assert destination.read_text(encoding="utf-8") == "previous"
    assert [path.name for path in tmp_path.iterdir()] == ["report.xlsx"]
