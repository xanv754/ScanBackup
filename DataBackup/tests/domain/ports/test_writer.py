import unittest
from pathlib import Path
from unittest.mock import patch
from scanbackup.domain.ports.writer import BaseWriter


class _DummyWriter(BaseWriter):
    """Minimal concrete writer used only to exercise BaseWriter's shared logic."""

    def export(self, filename, data):
        return str(self.dir / filename)


class TestBaseWriter(unittest.TestCase):
    """Unit tests for the BaseWriter shared home-directory resolution."""

    def test_cannot_be_instantiated_directly(self) -> None:
        """An ABC with an unimplemented abstract method must not be instantiable."""
        with self.assertRaises(TypeError):
            BaseWriter()

    def test_uses_given_directory_when_provided(self) -> None:
        """An explicit directory must be kept as-is, skipping home resolution."""
        writer = _DummyWriter(dir=Path("/custom/dir"))
        self.assertEqual(writer.dir, Path("/custom/dir"))

    @patch("scanbackup.domain.ports.writer.Path.home")
    def test_defaults_to_downloads_when_it_exists(self, mock_home) -> None:
        """Downloads must be preferred when it exists under the home directory."""
        fake_home = Path("/fake/home")
        mock_home.return_value = fake_home
        with patch.object(Path, "exists", lambda self: self == fake_home / "Downloads"):
            writer = _DummyWriter()
        self.assertEqual(writer.dir, Path(str(fake_home / "Downloads")))

    @patch("scanbackup.domain.ports.writer.Path.home")
    def test_defaults_to_descargas_when_downloads_missing(self, mock_home) -> None:
        """Descargas must be used when Downloads does not exist but Descargas does."""
        fake_home = Path("/fake/home")
        mock_home.return_value = fake_home
        with patch.object(Path, "exists", lambda self: self == fake_home / "Descargas"):
            writer = _DummyWriter()
        self.assertEqual(writer.dir, Path(str(fake_home / "Descargas")))

    @patch("scanbackup.domain.ports.writer.Path.home")
    def test_defaults_to_home_when_no_download_dir_exists(self, mock_home) -> None:
        """The home directory itself must be used as a last resort."""
        fake_home = Path("/fake/home")
        mock_home.return_value = fake_home
        with patch.object(Path, "exists", lambda self: False):
            writer = _DummyWriter()
        self.assertEqual(writer.dir, Path(str(fake_home)))


if __name__ == "__main__":
    unittest.main()
