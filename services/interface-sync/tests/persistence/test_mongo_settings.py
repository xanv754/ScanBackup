import pytest

from interface_sync.exceptions import MissingDatabaseSettingsError
from interface_sync.persistence import MongoSettings

ALL_VARIABLES = (
    "MONGO_HOST",
    "MONGO_PORT",
    "MONGO_USERNAME",
    "MONGO_PASSWORD",
    "MONGO_DATABASE",
    "MONGO_AUTH_SOURCE",
)


@pytest.fixture
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for variable in ALL_VARIABLES:
        monkeypatch.delenv(variable, raising=False)
    return monkeypatch


@pytest.fixture
def full_environment(clean_environment: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    clean_environment.setenv("MONGO_HOST", "mongo")
    clean_environment.setenv("MONGO_PORT", "27017")
    clean_environment.setenv("MONGO_USERNAME", "admin")
    clean_environment.setenv("MONGO_PASSWORD", "s3cret")
    clean_environment.setenv("MONGO_DATABASE", "scan_backup")
    clean_environment.setenv("MONGO_AUTH_SOURCE", "other")
    return clean_environment


def test_settings_are_read_from_the_environment(full_environment: pytest.MonkeyPatch):
    """The connection settings come only from environment variables."""
    settings = MongoSettings.from_environment()

    assert settings.host == "mongo"
    assert settings.port == 27017
    assert settings.username == "admin"
    assert settings.password == "s3cret"
    assert settings.database == "scan_backup"
    assert settings.auth_source == "other"


def test_auth_source_defaults_to_admin_when_absent(full_environment: pytest.MonkeyPatch):
    """MONGO_AUTH_SOURCE is optional and defaults to the admin database."""
    full_environment.delenv("MONGO_AUTH_SOURCE")

    assert MongoSettings.from_environment().auth_source == "admin"


def test_password_is_hidden_from_repr(full_environment: pytest.MonkeyPatch):
    """Secrets never reach logs: the password is not part of repr."""
    assert "s3cret" not in repr(MongoSettings.from_environment())


def test_missing_variables_are_all_named(clean_environment: pytest.MonkeyPatch):
    """Every absent required variable is reported in one error."""
    with pytest.raises(MissingDatabaseSettingsError) as error:
        MongoSettings.from_environment()

    for variable in ALL_VARIABLES[:-1]:
        assert variable in str(error.value)


def test_a_single_missing_variable_is_reported(full_environment: pytest.MonkeyPatch):
    """Only the absent variable is named."""
    full_environment.delenv("MONGO_PASSWORD")

    with pytest.raises(MissingDatabaseSettingsError) as error:
        MongoSettings.from_environment()

    assert "MONGO_PASSWORD" in str(error.value)
    assert "MONGO_HOST" not in str(error.value)


def test_empty_variable_counts_as_missing(full_environment: pytest.MonkeyPatch):
    """An empty variable is treated like an absent one."""
    full_environment.setenv("MONGO_DATABASE", "")

    with pytest.raises(MissingDatabaseSettingsError, match="MONGO_DATABASE"):
        MongoSettings.from_environment()


@pytest.mark.parametrize("port", ["abc", "0", "-5", "70000", "27.017"])
def test_invalid_port_is_rejected(full_environment: pytest.MonkeyPatch, port: str):
    """A port that is not a number in 1..65535 is a settings error, not an unexpected crash."""
    full_environment.setenv("MONGO_PORT", port)

    with pytest.raises(MissingDatabaseSettingsError, match="MONGO_PORT"):
        MongoSettings.from_environment()
