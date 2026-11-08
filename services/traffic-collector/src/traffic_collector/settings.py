from collections.abc import Mapping
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from traffic_collector.constants.constants import (
    CONFIG_PATH_VARIABLE,
    DEFAULT_CONFIG_PATH,
    DEFAULT_MONGO_AUTH_SOURCE,
    MONGO_AUTH_SOURCE_VARIABLE,
    MONGO_DATABASE_VARIABLE,
    MONGO_HOST_VARIABLE,
    MONGO_PASSWORD_VARIABLE,
    MONGO_PORT_VARIABLE,
    MONGO_USERNAME_VARIABLE,
    SCAN_PASSWORD_VARIABLE,
    SCAN_USERNAME_VARIABLE,
    TEXT_ENCODING,
)
from traffic_collector.constants.enums import ValidationErrorType
from traffic_collector.exceptions import InvalidSettingsError


class CollectionConfig(BaseModel):
    """Tunable values of the collection, read from `config.yml`."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    max_concurrent_requests: int = Field(gt=0)
    request_timeout_seconds: float = Field(gt=0)
    max_consecutive_failures: int = Field(gt=0)


class ScanCredentials(BaseModel):
    """Basic-auth credentials of SCAN. The password is hidden from `repr`."""

    model_config = ConfigDict(frozen=True)

    username: str = Field(min_length=1)
    password: str = Field(min_length=1, repr=False)


class MongoSettings(BaseModel):
    """Connection settings of MongoDB. The password is hidden from `repr`."""

    model_config = ConfigDict(frozen=True)

    host: str = Field(min_length=1)
    port: int = Field(gt=0, le=65535)
    username: str = Field(min_length=1)
    password: str = Field(min_length=1, repr=False)
    database: str = Field(min_length=1)
    auth_source: str = Field(min_length=1)


class Settings(BaseModel):
    """Everything the service needs to start: configuration, SCAN and MongoDB access."""

    model_config = ConfigDict(frozen=True)

    collection: CollectionConfig
    scan: ScanCredentials
    mongo: MongoSettings


class SettingsLoader:
    """Builds and validates `Settings` from `config.yml` and the environment.

    Secrets come only from the environment. Every invalid value is accumulated and reported
    together through `InvalidSettingsError`, which the process maps to a general error.
    """

    def __init__(self, environment: Mapping[str, str]) -> None:
        """Receive the environment to read (injected instead of reading `os.environ`)."""
        self._environment = environment

    def load(self) -> Settings:
        """Return the validated settings or raise `InvalidSettingsError` with all the causes."""
        causes: list[str] = []
        config_values = self._read_config(causes)
        collection = (
            None
            if config_values is None
            else self._build(CollectionConfig, config_values, "config.yml", causes)
        )
        scan = self._build(ScanCredentials, self._scan_values(), "SCAN", causes)
        mongo = self._build(MongoSettings, self._mongo_values(), "MongoDB", causes)
        if causes or collection is None or scan is None or mongo is None:
            raise InvalidSettingsError(causes)
        return Settings(collection=collection, scan=scan, mongo=mongo)

    def _read_config(self, causes: list[str]) -> dict | None:
        """Parse `config.yml`; record the cause and return None if the file is unusable."""
        config_path = Path(self._environment.get(CONFIG_PATH_VARIABLE) or DEFAULT_CONFIG_PATH)
        try:
            content = yaml.safe_load(config_path.read_text(encoding=TEXT_ENCODING))
        except (OSError, UnicodeDecodeError) as error:
            causes.append(f"No se puede leer el archivo {config_path} ({error})")
            return None
        except yaml.YAMLError as error:
            reason = " ".join(str(error).split())
            causes.append(f"El archivo {config_path} no es YAML válido ({reason})")
            return None
        if not isinstance(content, dict):
            causes.append(f"El archivo {config_path} debe ser un mapeo de claves y valores")
            return None
        return content

    def _scan_values(self) -> dict[str, str]:
        """Return the SCAN credentials found in the environment (empty when absent)."""
        return {
            "username": self._environment.get(SCAN_USERNAME_VARIABLE, ""),
            "password": self._environment.get(SCAN_PASSWORD_VARIABLE, ""),
        }

    def _mongo_values(self) -> dict[str, str]:
        """Return the MongoDB values found in the environment (empty when absent)."""
        return {
            "host": self._environment.get(MONGO_HOST_VARIABLE, ""),
            "port": self._environment.get(MONGO_PORT_VARIABLE, ""),
            "username": self._environment.get(MONGO_USERNAME_VARIABLE, ""),
            "password": self._environment.get(MONGO_PASSWORD_VARIABLE, ""),
            "database": self._environment.get(MONGO_DATABASE_VARIABLE, ""),
            "auth_source": (
                self._environment.get(MONGO_AUTH_SOURCE_VARIABLE) or DEFAULT_MONGO_AUTH_SOURCE
            ),
        }

    @staticmethod
    def _build[ModelT: BaseModel](
        model: type[ModelT], values: dict, source: str, causes: list[str]
    ) -> ModelT | None:
        """Validate `values` against `model`; record one cause per invalid field.

        The cause names the field only, never its value, so secrets are not exposed.
        """
        try:
            return model.model_validate(values)
        except ValidationError as error:
            causes.extend(
                f"{source}: '{'.'.join(str(part) for part in detail['loc'])}' "
                f"{SettingsLoader._describe(detail['type'])}"
                for detail in error.errors()
            )
            return None

    @staticmethod
    def _describe(error_type: str) -> str:
        """Return the cause text for a validation error type."""
        if error_type in (ValidationErrorType.MISSING, ValidationErrorType.STRING_TOO_SHORT):
            return "ausente o vacío"
        if error_type == ValidationErrorType.EXTRA_FORBIDDEN:
            return "clave no reconocida"
        return "valor inválido"
