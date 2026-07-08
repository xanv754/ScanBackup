from scanbackup.utils.configuration.env import Environment


class UserEnvironment(Environment):
    """A class that inherits from `Environment` to get the user SCAN from environment variables."""

    def __init__(self, dev: bool = False, testing: bool = False) -> None:
        super().__init__(dev, testing)

    def get_username(self) -> str | None:
        """Gets the database username of SCAN from the environment variables.

        :return str | None: The database username of SCAN if found, otherwise `None`.
        """
        return self.get_env("SCAN_USERNAME")

    def get_password(self) -> str | None:
        """Gets the database password of SCAN from the environment variables.

        :return str | None: The database password of SCAN if found, otherwise `None`.
        """
        return self.get_env("SCAN_PASSWORD")
