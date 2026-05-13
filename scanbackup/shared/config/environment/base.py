from os import path
from typing import Dict
from dotenv import load_dotenv, dotenv_values
from scanbackup.shared.config.metadata import BASE_ENV, PROD_ENV, DEV_ENV, TEST_ENV
from scanbackup.shared.errors.config.env import (
    EnvConfigError,
    EnvFileNotFoundError,
    MissingEnvironmentVariableError,
)
from scanbackup.shared.config.paths import PathConfig

load_dotenv(override=True)


class BaseEnvironment:
    """A parent class that handles the declaration of environment variables."""

    _env: Dict[str, str | None] | None
    _base_path: str = PathConfig.FOLDER_ROOT.resolve()

    def __init__(self, dev: bool, test: bool) -> None:
        self._env = self._get_env_file(dev, test)

    def _get_env_file(self, dev: bool, test: bool) -> Dict[str, str | None]:
        """Load variables from the specified environment.

        :returns Dict[str, str | None]: Dictionary containing the environment variables.
        """
        try:
            if dev:
                if not path.exists(path.join(self._base_path, DEV_ENV)):
                    raise EnvFileNotFoundError(error=DEV_ENV)
                return dotenv_values(path.join(self._base_path, DEV_ENV))
            elif test:
                if not path.exists(path.join(self._base_path, TEST_ENV)):
                    raise EnvFileNotFoundError(error=TEST_ENV)
                return dotenv_values(path.join(self._base_path, TEST_ENV))
            else:
                if path.exists(path.join(self._base_path, PROD_ENV)):
                    return dotenv_values(path.join(self._base_path, PROD_ENV))
                elif path.exists(path.join(self._base_path, BASE_ENV)):
                    return dotenv_values(path.join(self._base_path, BASE_ENV))
                else:
                    raise EnvFileNotFoundError(error=f"{BASE_ENV} o {PROD_ENV}")
        except EnvFileNotFoundError:
            exit(1)
        except Exception as error:
            raise EnvConfigError(error=error)

    def get_env(self, name: str) -> str | None:
        """Gets the URL to update the sources.

        :return str | None: URL if found, otherwise `None`.
        """
        try:
            if self._env:
                env = self._env.get(name)
                if not env:
                    raise MissingEnvironmentVariableError(var_name=name)
                return env
            raise MissingEnvironmentVariableError()
        except MissingEnvironmentVariableError:
            exit(1)
        except Exception as error:
            raise EnvConfigError(error=error)
