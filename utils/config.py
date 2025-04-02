import os
from dotenv import load_dotenv
from utils.log import LogHandler


load_dotenv(override=True)


class ConfigurationHandler:
    """Handler to get all configuration to system."""

    __instance: "ConfigurationHandler | None" = None
    uri_postgres: str

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(ConfigurationHandler, cls).__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        try:
            if not hasattr(self, "__initialized"):
                self.__initialized = True
                filepath_env = os.path.realpath("./") + "/.env"
                if not os.path.isfile(filepath_env):
                    raise FileNotFoundError("Enviroment file not found.")
                uri = os.getenv("URI")
                if not uri:
                    raise ValueError("URI variable not found in enviroment file.")
                self.uri_postgres = uri
        except Exception as e:
            LogHandler.log(message=f"Failed to obtain configuration. {e}", path=__file__, err=True)
            exit(1)

    @classmethod
    def set_uri(cls, uri: str) -> "ConfigurationHandler":
        """Set the URI database.

        Parameters
        ----------
        uri : str
            URI database.
        """
        instance = cls.__new__(cls)
        instance.__init__()
        instance.uri_postgres = uri
        return instance


if __name__ == "__main__":
    config_uno = ConfigurationHandler()
    print(config_uno.uri_postgres)
    config_two = ConfigurationHandler.set_uri("tumama")
    print(config_two.uri_postgres)
