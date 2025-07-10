import os
from dotenv import load_dotenv, dotenv_values
from systemgrd.utils.log import log


load_dotenv(override=True)


class ConfigurationHandler:
    """Handler to get all configuration to system."""

    __instance: "ConfigurationHandler | None" = None
    uri_postgres: str
    uri_mongo: str

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(ConfigurationHandler, cls).__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        try:
            if not hasattr(self, "__initialized"):
                self.__initialized = True
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                if os.path.exists(f"{base_path}/.env.development"):
                    env = dotenv_values(f"{base_path}/.env.development")
                elif os.path.exists(f"{base_path}/.env.test"):
                    env = dotenv_values(f"{base_path}/.env.test")
                elif os.path.exists(f"{base_path}/.env.production"):
                    env = dotenv_values(f"{base_path}/.env.production")
                elif os.path.exists(f"{base_path}/.env"):
                    env = dotenv_values(f"{base_path}/.env")
                else:
                    raise FileNotFoundError("No file with environment variables found")
                uri_mongo = env.get("URI_MONGO")
                if uri_mongo: 
                    self.uri_mongo = uri_mongo
                else:
                    log.warning(message=f"Failed to obtain configuration. URI MongoDB variable not found in enviroment file")
        except Exception as e:
            log.error(message=f"Failed to obtain configuration. {e}")
            exit(1)


if __name__ == "__main__":
    config = ConfigurationHandler()
    print(config.uri_mongo)
