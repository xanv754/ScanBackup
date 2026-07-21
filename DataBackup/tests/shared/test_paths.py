import os
import unittest
from pathlib import Path
from scanbackup.shared.paths import SCANBACKUP_HOME_ENV_VAR, get_project_root
from tests.support import TempDirTestCase


class TestGetProjectRoot(TempDirTestCase):
    """Unit tests for the SCANBACKUP_HOME-aware project root resolver."""

    def setUp(self) -> None:
        """Ensure SCANBACKUP_HOME is unset before each test."""
        super().setUp()
        self._original_env = os.environ.pop(SCANBACKUP_HOME_ENV_VAR, None)

    def tearDown(self) -> None:
        """Restore the original SCANBACKUP_HOME environment state."""
        if self._original_env is None:
            os.environ.pop(SCANBACKUP_HOME_ENV_VAR, None)
        else:
            os.environ[SCANBACKUP_HOME_ENV_VAR] = self._original_env
        super().tearDown()

    def test_falls_back_to_repository_root_when_env_var_unset(self) -> None:
        """Without SCANBACKUP_HOME, it must resolve to the repository root."""
        root = get_project_root()
        self.assertTrue((root / "pyproject.toml").is_file())

    def test_uses_scanbackup_home_when_set(self) -> None:
        """With SCANBACKUP_HOME set, it must resolve to that directory."""
        os.environ[SCANBACKUP_HOME_ENV_VAR] = str(self.tmp_dir)
        root = get_project_root()
        self.assertEqual(root, Path(self.tmp_dir).resolve())


if __name__ == "__main__":
    unittest.main()
