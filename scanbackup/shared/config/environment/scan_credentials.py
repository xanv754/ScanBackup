from pydantic import BaseModel
from scanbackup.shared.config.environment.base import BaseEnvironment
from scanbackup.shared.config.metadata import (
    USERNAME_SCAN_CREDENTIALS,
    PASSWORD_SCAN_CREDENTIALS,
)


class ScanCredentialSchema(BaseModel):
    username: str
    password: str


class ScanCredentialEnvironment(BaseEnvironment):
    """A class that inherits from `Environment` to get the SCAN credentials from environment variables."""

    def __init__(self, dev: bool = False, testing: bool = False) -> None:
        super().__init__(dev, testing)

    def get_credentials(self) -> ScanCredentialSchema:
        """Gets the SCAN credentials from the environment variables.

        :return ScanCredentialSchema: SCAN credentials.
        """
        return ScanCredentialSchema(
            username=self.get_env(USERNAME_SCAN_CREDENTIALS),
            password=self.get_env(PASSWORD_SCAN_CREDENTIALS),
        )
