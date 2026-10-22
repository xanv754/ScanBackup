import pytest

from interface_sync.exceptions import MissingCredentialsError
from interface_sync.models import ScanCredentials


def test_credentials_are_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """RF-003: basic-auth credentials come from SCAN_USERNAME and SCAN_PASSWORD."""
    monkeypatch.setenv("SCAN_USERNAME", "operator")
    monkeypatch.setenv("SCAN_PASSWORD", "secret")

    credentials = ScanCredentials.from_environment()

    assert credentials.username == "operator"
    assert credentials.password == "secret"


def test_password_is_hidden_from_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    """RF-014: secrets must never reach logs or terminal."""
    monkeypatch.setenv("SCAN_USERNAME", "operator")
    monkeypatch.setenv("SCAN_PASSWORD", "secret")

    assert "secret" not in repr(ScanCredentials.from_environment())


@pytest.mark.parametrize(
    ("username", "password", "missing_variable"),
    [
        (None, "secret", "SCAN_USERNAME"),
        ("operator", None, "SCAN_PASSWORD"),
        ("", "secret", "SCAN_USERNAME"),
        ("operator", "", "SCAN_PASSWORD"),
    ],
)
def test_missing_or_empty_credential_raises(
    monkeypatch: pytest.MonkeyPatch,
    username: str | None,
    password: str | None,
    missing_variable: str,
) -> None:
    """RF-003: an absent or empty credential raises a specific error naming the variable."""
    for variable, value in (("SCAN_USERNAME", username), ("SCAN_PASSWORD", password)):
        if value is None:
            monkeypatch.delenv(variable, raising=False)
        else:
            monkeypatch.setenv(variable, value)

    with pytest.raises(MissingCredentialsError, match=missing_variable):
        ScanCredentials.from_environment()


def test_both_missing_credentials_are_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    """RF-003: every missing variable is reported in one error."""
    monkeypatch.delenv("SCAN_USERNAME", raising=False)
    monkeypatch.delenv("SCAN_PASSWORD", raising=False)

    with pytest.raises(MissingCredentialsError) as error_info:
        ScanCredentials.from_environment()

    assert "SCAN_USERNAME" in str(error_info.value)
    assert "SCAN_PASSWORD" in str(error_info.value)
