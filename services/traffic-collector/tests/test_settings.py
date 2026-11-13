from pathlib import Path

import pytest

from traffic_collector.constants.constants import CONFIG_PATH_VARIABLE
from traffic_collector.exceptions import InvalidSettingsError
from traffic_collector.settings import SettingsLoader

VALID_CONFIG = "max_concurrent_requests: 5\nrequest_timeout_seconds: 30\nmax_consecutive_failures: 5\n"


@pytest.fixture
def environment(tmp_path: Path) -> dict[str, str]:
    """A complete valid environment pointing to a valid config file."""
    config_path = tmp_path / "config.yml"
    config_path.write_text(VALID_CONFIG, encoding="utf-8")
    return {
        CONFIG_PATH_VARIABLE: str(config_path),
        "SCAN_USERNAME": "user",
        "SCAN_PASSWORD": "secret",
        "MONGO_HOST": "mongo",
        "MONGO_PORT": "27017",
        "MONGO_USERNAME": "root",
        "MONGO_PASSWORD": "mongo-secret",
        "MONGO_DATABASE": "scan_backup",
    }


def write_config(environment: dict[str, str], content: str) -> None:
    """Overwrite the config file the environment points to."""
    Path(environment[CONFIG_PATH_VARIABLE]).write_text(content, encoding="utf-8")


def test_valid_settings_are_loaded(environment: dict[str, str]) -> None:
    """Valid configuration and environment produce typed settings (RF-016, RF-022, RF-027)."""
    settings = SettingsLoader(environment).load()

    assert settings.collection.max_concurrent_requests == 5
    assert settings.collection.request_timeout_seconds == 30
    assert settings.collection.max_consecutive_failures == 5
    assert settings.mongo.port == 27017
    assert settings.mongo.auth_source == "admin"


def test_missing_config_file_is_invalid(environment: dict[str, str]) -> None:
    """A missing config file is a general error (RF-028)."""
    environment[CONFIG_PATH_VARIABLE] += ".missing"

    with pytest.raises(InvalidSettingsError) as error:
        SettingsLoader(environment).load()

    assert len(error.value.causes) == 1


def test_non_yaml_config_is_invalid(environment: dict[str, str]) -> None:
    """A config file that is not YAML is a general error (RF-028)."""
    write_config(environment, "key: [unclosed")

    with pytest.raises(InvalidSettingsError):
        SettingsLoader(environment).load()


def test_non_mapping_config_is_invalid(environment: dict[str, str]) -> None:
    """A config file that is not a mapping is a general error (RF-028)."""
    write_config(environment, "- one\n- two\n")

    with pytest.raises(InvalidSettingsError):
        SettingsLoader(environment).load()


@pytest.mark.parametrize(
    "content",
    [
        "request_timeout_seconds: 30\nmax_consecutive_failures: 5\n",
        VALID_CONFIG.replace(
            "max_concurrent_requests: 5", "max_concurrent_requests: 0"
        ),
        VALID_CONFIG.replace(
            "request_timeout_seconds: 30", "request_timeout_seconds: -1"
        ),
        VALID_CONFIG.replace(
            "max_consecutive_failures: 5", "max_consecutive_failures: true"
        ),
        VALID_CONFIG.replace(
            "max_concurrent_requests: 5", "max_concurrent_requests: '5'"
        ),
        VALID_CONFIG + "unknown_key: 1\n",
    ],
    ids=["missing", "zero", "negative", "boolean", "text", "unknown-key"],
)
def test_invalid_config_values_are_rejected(
    environment: dict[str, str], content: str
) -> None:
    """Missing, non-positive, mistyped or unknown keys are a general error (RF-028)."""
    write_config(environment, content)

    with pytest.raises(InvalidSettingsError):
        SettingsLoader(environment).load()


@pytest.mark.parametrize(
    "variable",
    [
        "SCAN_USERNAME",
        "SCAN_PASSWORD",
        "MONGO_HOST",
        "MONGO_PORT",
        "MONGO_USERNAME",
        "MONGO_PASSWORD",
        "MONGO_DATABASE",
    ],
)
def test_missing_environment_variable_is_invalid(
    environment: dict[str, str], variable: str
) -> None:
    """A missing credential or database variable is a general error (RF-028)."""
    del environment[variable]

    with pytest.raises(InvalidSettingsError):
        SettingsLoader(environment).load()


def test_invalid_mongo_port_is_rejected(environment: dict[str, str]) -> None:
    """A non-numeric MongoDB port is a general error (RF-028)."""
    environment["MONGO_PORT"] = "abc"

    with pytest.raises(InvalidSettingsError):
        SettingsLoader(environment).load()


def test_all_causes_are_reported_together(environment: dict[str, str]) -> None:
    """Every invalid value is reported in a single error (RF-028)."""
    del environment["SCAN_PASSWORD"]
    del environment["MONGO_DATABASE"]
    write_config(environment, VALID_CONFIG + "unknown_key: 1\n")

    with pytest.raises(InvalidSettingsError) as error:
        SettingsLoader(environment).load()

    assert len(error.value.causes) == 3


def test_secrets_are_not_exposed(environment: dict[str, str]) -> None:
    """Passwords never appear in repr or in the causes of an error (RF-028)."""
    settings = SettingsLoader(environment).load()
    assert "secret" not in repr(settings)

    environment["MONGO_PORT"] = "abc"
    environment["SCAN_USERNAME"] = ""
    with pytest.raises(InvalidSettingsError) as error:
        SettingsLoader(environment).load()
    assert "secret" not in str(error.value)
    assert "abc" not in str(error.value)
