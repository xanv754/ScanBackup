from systemgrd.utils.configuration.env import Environment


class URIEnvironment(Environment):
    """A class that inherits from `Environment` to get the database URI from environment variables."""

    def __init__(
        self, prod: bool = False, dev: bool = False, testing: bool = False
    ) -> None:
        super().__init__(prod, dev, testing)

    def get_uri_db(self) -> str:
        """Gets the database URI from the environment variables.

        :return str: The database URI if found.
        """
        return self.get_env("URI_MONGO", optional=False)