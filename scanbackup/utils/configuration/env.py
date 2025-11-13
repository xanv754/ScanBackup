from os import path
from typing import Dict
from dotenv import load_dotenv, dotenv_values
from scanbackup.utils.configuration.log import log


load_dotenv(override=True)


class Environment:
    """A parent class that handles the declaration of environment variables."""

    _env: Dict[str, str | None] | None
    _base_path: str = path.abspath(path.join(path.dirname(__file__), "..", "..", ".."))

    def __init__(
        self, dev: bool = False, test: bool = False
    ) -> None:
        self._env = self._get_env_file(dev, test)

    def _get_env_file(
        self, dev: bool = False, test: bool = False
    ) -> Dict[str, str | None]:
        """Load variables from the specified environment.

        :returns Dict[str, str | None]: Dictionary containing the environment variables.
        """
        try:
            if dev:
                if not path.exists(path.join(self._base_path, ".env.development")):
                    raise FileNotFoundError(
                        f"El archivo 'env.development' es requerido"
                    )
                return dotenv_values(path.join(self._base_path, ".env.development"))
            elif test:
                if not path.exists(path.join(self._base_path, ".env.testing")):
                    raise FileNotFoundError(f"El archivo 'env.testing' es requerido")
                return dotenv_values(path.join(self._base_path, ".env.testing"))
            else:
                if not path.exists(
                    path.join(self._base_path, ".env.production")
                ) or path.exists(path.join(self._base_path, ".env")):
                    raise FileNotFoundError(
                        f"El archivo 'env.production' o '.env' es requerido"
                    )
                return dotenv_values(path.join(self._base_path, ".env.production"))
        except FileNotFoundError as error:
            log.error(
                f"Archivo con variables de entorno no encontrado en {self._base_path} - {error}"
            )
            exit(1)
        except Exception as error:
            log.error(f"Error en las variables de entorno del sistema - {error}")
            exit(1)
            
    def get_env(self, name: str, optional: bool = True) -> str | None:
        """Gets the URL to update the sources.

        :return str | None: URL if found, otherwise `None`.
        """
        try:
            if self._env:
                env = self._env.get(name)
                if not env:
                    raise Exception(f"Variable {name} no declarada")
                return env
            raise Exception("No se ha podido encontrar las variables de entorno")
        except Exception as error:
            log.error(f"No se ha encontrado las variables de entorno requeridas - {error}")
            if optional: return None
            exit(1)