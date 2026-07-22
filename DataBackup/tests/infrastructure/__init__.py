import sys
from types import ModuleType
from unittest.mock import MagicMock

# `scanbackup.infrastructure.cli.sources.updater` imports the external `sources_scrapper`
# package, which is not an installed dependency of this project. Any test that
# transitively imports `scanbackup.infrastructure` (its __init__ eagerly wires the whole
# CLI tree) would fail with ModuleNotFoundError without this. Registering a fake module
# here, before test discovery imports any submodule of this package, keeps the whole
# `scanbackup.infrastructure` tree importable for testing.
if "sources_scrapper" not in sys.modules:
    fake_package = ModuleType("sources_scrapper")
    fake_submodule = ModuleType("sources_scrapper.scrapper_scanbackup")
    fake_submodule.UpdaterSources = MagicMock(name="UpdaterSources")
    fake_package.scrapper_scanbackup = fake_submodule
    sys.modules["sources_scrapper"] = fake_package
    sys.modules["sources_scrapper.scrapper_scanbackup"] = fake_submodule
