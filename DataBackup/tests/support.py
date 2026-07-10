import shutil
import unittest
from pathlib import Path

TMP_ROOT = Path(__file__).resolve().parent / "tmp"


class TempDirTestCase(unittest.TestCase):
    """Base test case that provides an isolated temporary directory per test.

    Subclasses that create files on disk should use ``self.tmp_dir`` as the
    target location. The directory is created before each test and removed
    after each test, so no test ever leaves residual files behind.
    """

    def setUp(self) -> None:
        """Create a fresh temporary directory scoped to this test case."""
        self.tmp_dir = TMP_ROOT / f"{self.__class__.__name__}_{self._testMethodName}"
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        """Remove the temporary directory created for this test."""
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
