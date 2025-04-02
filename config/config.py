from os import getenv, getcwd, path
from dotenv import load_dotenv
from utils.log import LogHandler


load_dotenv(override=True)


class ConfigurationHandler:
    """Handler to get all configuration to system."""

    uri_postgres: str

    #TODO: Add creation control for creating a new object of class.

    def __init__(self) -> None:
        try:
            filepath_env = getcwd() + "/.env"
            if not path.isfile(filepath_env):
                raise FileNotFoundError("Enviroment file not found.")
            uri_env = getenv("URI")
            if not uri_env:
                raise ValueError("URI variable not found in enviroment file.")
            self.uri_postgres = uri_env
        except Exception as e:
            LogHandler.log(message=str(e), path=__file__, err=True)


if __name__ == "__main__":
    config = ConfigurationHandler()
