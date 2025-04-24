import os
from dotenv import load_dotenv, dotenv_values
from utils.log import LogHandler


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
                if os.path.exists(".env.development"):
                    env = dotenv_values(".env.development")
                    uri_postgres = env.get("URI_POSTGRES")
                    if uri_postgres: 
                        self.uri_postgres = uri_postgres
                    else:
                        log = LogHandler()
                        log.export(message=f"Failed to obtain configuration. URI PostgreSQL variable not found in enviroment file", path=__file__, err=True)
                    uri_mongo = env.get("URI_MONGO")
                    if uri_mongo: 
                        self.uri_mongo = uri_mongo
                    else:
                        log = LogHandler()
                        log.export(message=f"Failed to obtain configuration. URI MongoDB variable not found in enviroment file", path=__file__, err=True)
                elif os.path.exists(".env.production"):
                    env = dotenv_values(".env.production")
                    uri_postgres = env.get("URI_POSTGRES")
                    if uri_postgres: 
                        self.uri_postgres = uri_postgres
                    else:
                        log = LogHandler()
                        log.export(message=f"Failed to obtain configuration. URI PostgreSQL variable not found in enviroment file", path=__file__, err=True)
                    uri_mongo = env.get("URI_MONGO")
                    if uri_mongo: 
                        self.uri_mongo = uri_mongo
                    else:
                        log = LogHandler()
                        log.export(message=f"Failed to obtain configuration. URI MongoDB variable not found in enviroment file", path=__file__, err=True)
                elif os.path.exists(".env"):
                    env = dotenv_values(".env")
                    uri_postgres = env.get("URI_POSTGRES")
                    if uri_postgres: 
                        self.uri_postgres = uri_postgres
                    else:
                        log = LogHandler()
                        log.export(message=f"Failed to obtain configuration. URI PostgreSQL variable not found in enviroment file", path=__file__, err=True)
                    uri_mongo = env.get("URI_MONGO")
                    if uri_mongo: 
                        self.uri_mongo = uri_mongo
                    else:
                        log = LogHandler()
                        log.export(message=f"Failed to obtain configuration. URI MongoDB variable not found in enviroment file", path=__file__, err=True)
                else:
                    raise FileNotFoundError("No file with environment variables found")
        except Exception as e:
            log = LogHandler()
            log.export(message=f"Failed to obtain configuration. {e}", path=__file__, err=True)
            exit(1)

    @classmethod
    def set_uri(cls, uri_postgres: str | None = None, uri_mongo: str | None = None) -> "ConfigurationHandler":
        """Set the URI database.

        Parameters
        ----------
        uri : str
            URI database.
        """
        instance = cls.__new__(cls)
        instance.__init__()
        if uri_postgres:
            instance.uri_postgres = uri_postgres
        if uri_mongo:
            instance.uri_mongo = uri_mongo
        return instance