import os
from pathlib import Path

import pytest

from reports.exceptions import InvalidSettingsError
from reports.settings import Settings, SettingsLoader
from tests.conftest import MONGO_ENVIRONMENT


def write_config(directory: Path, content: str) -> Path:
    """Write `content` as the config file inside `directory` and return its path."""
    config_path = directory / "config.yml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


def build_environment(config_path: Path, **overrides: str) -> dict[str, str]:
    """Return a valid environment pointing to `config_path`, with `overrides` applied."""
    return {**MONGO_ENVIRONMENT, "CONFIG_PATH": str(config_path), **overrides}


def reports_section(**values: str) -> str:
    """Build a config text with the given `metadata.reports` values."""
    lines = ["metadata:", "  reports:"]
    lines.extend(f"    {key}: '{value}'" for key, value in values.items())
    if not values:
        lines.append("    {}")
    return "\n".join(lines) + "\n"


def load_causes(environment: dict[str, str]) -> list[str]:
    """Load the settings expecting failure and return the causes."""
    with pytest.raises(InvalidSettingsError) as error_info:
        SettingsLoader(environment).load()
    return error_info.value.causes


def load(config_text: str, tmp_path: Path) -> Settings:
    """Load valid settings from `config_text`."""
    return SettingsLoader(build_environment(write_config(tmp_path, config_text))).load()


def test_rf032_valid_config_is_loaded(tmp_path: Path, export_directory: Path) -> None:
    """RF-032: the three keys are read from `metadata.reports`."""
    text = reports_section(
        prefix_name="Weekly",
        date_format="%Y-%m-%d",
        export_path=str(export_directory),
    )
    settings = load(text, tmp_path)
    assert settings.report.prefix_name == "Weekly"
    assert settings.report.date_format == "%Y-%m-%d"
    assert settings.report.export_path == export_directory


def test_rf032_omitted_keys_use_defaults(
    tmp_path: Path, export_directory: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RF-032: omitted keys fall back to ScanBackup, %Y%m%d_%H%M%S and `~`."""
    monkeypatch.setenv("HOME", str(export_directory))
    settings = load("metadata:\n  reports: {}\n", tmp_path)
    assert settings.report.prefix_name == "ScanBackup"
    assert settings.report.date_format == "%Y%m%d_%H%M%S"
    assert settings.report.export_path == export_directory


def test_rf032_empty_file_means_all_defaults(
    tmp_path: Path, export_directory: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RF-032: an empty file (`safe_load` returns None) equals the defaults."""
    monkeypatch.setenv("HOME", str(export_directory))
    assert load("", tmp_path).report.prefix_name == "ScanBackup"


def test_rf032_home_is_expanded_in_export_path(
    tmp_path: Path, export_directory: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RF-032: a leading `~` expands to the home directory of the user."""
    monkeypatch.setenv("HOME", str(export_directory))
    settings = load('metadata:\n  reports:\n    export_path: "~"\n', tmp_path)
    assert settings.report.export_path == export_directory


def test_rf032_missing_file_is_invalid(tmp_path: Path) -> None:
    """RF-032: a config file that does not exist is invalid."""
    causes = load_causes(build_environment(tmp_path / "missing.yml"))
    assert any("No se puede leer" in cause for cause in causes)


def test_rf032_invalid_yaml_is_invalid(tmp_path: Path) -> None:
    """RF-032: a file that is not valid YAML is invalid."""
    causes = load_causes(build_environment(write_config(tmp_path, "metadata: [unclosed")))
    assert any("no es YAML válido" in cause for cause in causes)


def test_rf032_root_must_be_a_mapping(tmp_path: Path) -> None:
    """RF-032: a root that is not a mapping is invalid."""
    causes = load_causes(build_environment(write_config(tmp_path, "- a\n- b\n")))
    assert any("mapeo" in cause for cause in causes)


@pytest.mark.parametrize(
    ("content", "unknown_key"),
    [
        ("extra: 1\n", "extra"),
        ("metadata:\n  other: 1\n", "metadata.other"),
        ("metadata:\n  reports:\n    unknown: 1\n", "metadata.reports.unknown"),
    ],
)
def test_rf032_unknown_keys_are_invalid_at_every_level(
    tmp_path: Path, content: str, unknown_key: str
) -> None:
    """RF-032: any key that is not recognized is invalid, at any level."""
    causes = load_causes(build_environment(write_config(tmp_path, content)))
    assert any(f"'{unknown_key}'" in cause for cause in causes)


@pytest.mark.parametrize(
    "prefix", ["", "   ", "a/b", "a\\b", "a:b", "a*b", "a?b", '"', "<>", "a|b"]
)
def test_rf032_invalid_prefix_name(tmp_path: Path, export_directory: Path, prefix: str) -> None:
    """RF-032: prefix_name cannot be empty, blank or contain forbidden file name characters."""
    text = reports_section(prefix_name=prefix, export_path=str(export_directory))
    causes = load_causes(build_environment(write_config(tmp_path, text)))
    assert any("prefix_name" in cause for cause in causes)


def test_rf032_prefix_name_must_be_text(tmp_path: Path) -> None:
    """RF-032: prefix_name that is not text is invalid."""
    causes = load_causes(
        build_environment(write_config(tmp_path, "metadata:\n  reports:\n    prefix_name: 12\n"))
    )
    assert any("prefix_name" in cause and "texto" in cause for cause in causes)


@pytest.mark.parametrize("date_format", ["%x", "%d/%m/%Y", "%Q", "%Y%", "%c"])
def test_rf032_invalid_date_format(
    tmp_path: Path, export_directory: Path, date_format: str
) -> None:
    """RF-032: unknown directives, a dangling `%` or forbidden output characters are invalid."""
    text = reports_section(date_format=date_format, export_path=str(export_directory))
    causes = load_causes(build_environment(write_config(tmp_path, text)))
    assert any("date_format" in cause for cause in causes)


def test_rf032_date_format_without_directives_is_valid(
    tmp_path: Path, export_directory: Path
) -> None:
    """RF-032: a format without directives is valid (the file name never changes)."""
    text = reports_section(date_format="fixed", export_path=str(export_directory))
    assert load(text, tmp_path).report.date_format == "fixed"


def test_rf032_date_format_must_be_text_and_not_empty(tmp_path: Path) -> None:
    """RF-032: date_format that is empty or not text is invalid."""
    empty = load_causes(
        build_environment(write_config(tmp_path, 'metadata:\n  reports:\n    date_format: ""\n'))
    )
    number = load_causes(
        build_environment(write_config(tmp_path, "metadata:\n  reports:\n    date_format: 5\n"))
    )
    assert any("vacío" in cause for cause in empty)
    assert any("texto" in cause for cause in number)


def test_rf032_missing_export_path_is_invalid_and_never_created(tmp_path: Path) -> None:
    """RF-032: export_path must exist; the service never creates it."""
    missing = tmp_path / "does-not-exist"
    text = reports_section(export_path=str(missing))
    causes = load_causes(build_environment(write_config(tmp_path, text)))
    assert any("export_path" in cause for cause in causes)
    assert not missing.exists()


def test_rf032_export_path_that_is_a_file_is_invalid(tmp_path: Path) -> None:
    """RF-032: export_path must be a directory."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")
    text = reports_section(export_path=str(file_path))
    causes = load_causes(build_environment(write_config(tmp_path, text)))
    assert any("export_path" in cause for cause in causes)


@pytest.mark.skipif(os.geteuid() == 0, reason="root can write anywhere")
def test_rf032_export_path_without_write_permission_is_invalid(tmp_path: Path) -> None:
    """RF-032: export_path must be writable by the user that runs the service."""
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o500)
    try:
        text = reports_section(export_path=str(locked))
        causes = load_causes(build_environment(write_config(tmp_path, text)))
    finally:
        locked.chmod(0o700)
    assert any("permiso de escritura" in cause for cause in causes)


def test_rf032_export_path_must_be_text_and_not_empty(tmp_path: Path) -> None:
    """RF-032: export_path that is empty or not text is invalid."""
    empty = load_causes(
        build_environment(write_config(tmp_path, 'metadata:\n  reports:\n    export_path: " "\n'))
    )
    number = load_causes(
        build_environment(write_config(tmp_path, "metadata:\n  reports:\n    export_path: 5\n"))
    )
    assert any("vacío" in cause for cause in empty)
    assert any("texto" in cause for cause in number)


def test_rf032_all_causes_are_accumulated(tmp_path: Path) -> None:
    """RF-032: every invalid value is reported together, not only the first one."""
    text = (
        "unknown: 1\n"
        "metadata:\n"
        "  reports:\n"
        '    prefix_name: ""\n'
        '    date_format: "%x"\n'
        f'    export_path: "{tmp_path / "missing"}"\n'
    )
    causes = load_causes(build_environment(write_config(tmp_path, text)))
    for expected in ("'unknown'", "prefix_name", "date_format", "export_path"):
        assert any(expected in cause for cause in causes)


def test_rf032_missing_mongo_variables_are_causes_without_secrets(
    tmp_path: Path, export_directory: Path
) -> None:
    """RF-032: missing database variables are reported; secret values never are."""
    config_path = write_config(tmp_path, reports_section(export_path=str(export_directory)))
    environment = build_environment(config_path, MONGO_HOST="", MONGO_PORT="not-a-number")
    causes = load_causes(environment)
    assert any("host" in cause for cause in causes)
    assert any("port" in cause for cause in causes)
    assert not any("secret-password" in cause for cause in causes)
