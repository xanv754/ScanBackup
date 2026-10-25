import os

from pydantic import BaseModel, ConfigDict, Field

from interface_sync.constants.constants import SCAN_PASSWORD_VARIABLE, SCAN_USERNAME_VARIABLE
from interface_sync.exceptions import MissingCredentialsError


class ScanCredentials(BaseModel):
    """Basic-auth credentials for SCAN. The password is hidden from `repr`."""

    model_config = ConfigDict(frozen=True)

    username: str = Field(min_length=1)
    password: str = Field(min_length=1, repr=False)

    @classmethod
    def from_environment(cls) -> "ScanCredentials":
        """Read the credentials from the environment; raise `MissingCredentialsError` if absent."""
        username = os.environ.get(SCAN_USERNAME_VARIABLE, "")
        password = os.environ.get(SCAN_PASSWORD_VARIABLE, "")
        missing = [
            variable
            for variable, value in (
                (SCAN_USERNAME_VARIABLE, username),
                (SCAN_PASSWORD_VARIABLE, password),
            )
            if not value
        ]
        if missing:
            raise MissingCredentialsError(f"Credenciales de SCAN ausentes: {', '.join(missing)}")
        return cls(username=username, password=password)
