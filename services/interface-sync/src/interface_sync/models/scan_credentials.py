import os
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from interface_sync.exceptions import MissingCredentialsError


class ScanCredentials(BaseModel):
    """Basic-auth credentials for SCAN. The password is hidden from `repr`."""

    model_config = ConfigDict(frozen=True)

    USERNAME_VARIABLE: ClassVar[str] = "SCAN_USERNAME"
    PASSWORD_VARIABLE: ClassVar[str] = "SCAN_PASSWORD"

    username: str = Field(min_length=1)
    password: str = Field(min_length=1, repr=False)

    @classmethod
    def from_environment(cls) -> "ScanCredentials":
        """Read the credentials from the environment; raise `MissingCredentialsError` if absent."""
        username = os.environ.get(cls.USERNAME_VARIABLE, "")
        password = os.environ.get(cls.PASSWORD_VARIABLE, "")
        missing = [
            variable
            for variable, value in (
                (cls.USERNAME_VARIABLE, username),
                (cls.PASSWORD_VARIABLE, password),
            )
            if not value
        ]
        if missing:
            raise MissingCredentialsError(
                f"Credenciales de SCAN ausentes: {', '.join(missing)}"
            )
        return cls(username=username, password=password)
