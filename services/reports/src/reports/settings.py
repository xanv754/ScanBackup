from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from reports.constants.constants import (
    CONFIG_METADATA_KEY,
    CONFIG_PATH_VARIABLE,
    CONFIG_REPORTS_KEY,
    CONFIG_REPORTS_KEYS,
    DEFAULT_CONFIG_PATH,
    DEFAULT_MONGO_AUTH_SOURCE,
    MONGO_AUTH_SOURCE_VARIABLE,
    MONGO_DATABASE_VARIABLE,
    MONGO_HOST_VARIABLE,
    MONGO_PASSWORD_VARIABLE,
    MONGO_PORT_VARIABLE,
    MONGO_USERNAME_VARIABLE,
    TEXT_ENCODING,
)
from reports.constants.enums import ValidationErrorType
from reports.exceptions import InvalidSettingsError
from reports.report_config import ReportConfig, ReportConfigValidator


class MongoSettings(BaseModel):
    """Connection settings of MongoDB. The password is hidden from `repr`."""

    model_config = ConfigDict(frozen=True)

    host: str = Field(min_length=1)
    port: int = Field(gt=0, le=65535)
    username: str = Field(min_length=1)
    password: str = Field(min_length=1, repr=False)
    database: str = Field(min_length=1)
    auth_source: str = Field(min_length=1)


@dataclass(frozen=True, slots=True)
class Settings:
    """Everything the service needs to start: the report configuration and MongoDB access."""

    report: ReportConfig
    mongo: MongoSettings


class SettingsLoader:
    """Builds and validates `Settings` from `config.yml` and the environment [RF-032].

    The database credentials come only from the environment. Every invalid value is
    accumulated and reported together through `InvalidSettingsError`.
    """

    def __init__(
        self, environment: Mapping[str, str], validator: ReportConfigValidator | None = None
    ) -> None:
        """Receive the environment to read (injected instead of reading `os.environ`)."""
        self._environment = environment
        self._validator = validator or ReportConfigValidator()

    def load(self) -> Settings:
        """Return the validated settings or raise `InvalidSettingsError` with all the causes."""
        causes: list[str] = []
        report = self._load_report_config(causes)
        mongo = self._build_mongo_settings(causes)
        if causes or report is None or mongo is None:
            raise InvalidSettingsError(causes)
        return Settings(report=report, mongo=mongo)

    def _load_report_config(self, causes: list[str]) -> ReportConfig | None:
        """Read `config.yml` and validate its `metadata.reports` section."""
        content = self._read_config_file(causes)
        if content is None:
            return None
        section = self._extract_reports_section(content, causes)
        if section is None:
            return None
        return self._validator.validate(section, causes)

    def _read_config_file(self, causes: list[str]) -> Mapping[str, object] | None:
        """Parse `config.yml`; an empty file is an empty mapping (all defaults)."""
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
        if content is None:
            return {}
        if not isinstance(content, dict):
            causes.append(f"El archivo {config_path} debe ser un mapeo de claves y valores")
            return None
        return content

    @staticmethod
    def _extract_reports_section(
        content: Mapping[str, object], causes: list[str]
    ) -> Mapping[str, object] | None:
        """Return `metadata.reports`, recording the unknown keys of every level.

        Unknown keys do not stop the validation of the known values, so that every cause is
        reported together. Only a section that is not a mapping returns None.
        """
        structure_cause_count = len(causes)
        metadata_values = SettingsLoader._mapping_or_cause(
            content.get(CONFIG_METADATA_KEY), CONFIG_METADATA_KEY, causes
        )
        reports_values = SettingsLoader._mapping_or_cause(
            metadata_values.get(CONFIG_REPORTS_KEY),
            f"{CONFIG_METADATA_KEY}.{CONFIG_REPORTS_KEY}",
            causes,
        )
        has_invalid_structure = len(causes) > structure_cause_count
        causes.extend(
            SettingsLoader._unknown_key_causes(content, (CONFIG_METADATA_KEY,), "")
            + SettingsLoader._unknown_key_causes(
                metadata_values, (CONFIG_REPORTS_KEY,), f"{CONFIG_METADATA_KEY}."
            )
            + SettingsLoader._unknown_key_causes(
                reports_values,
                CONFIG_REPORTS_KEYS,
                f"{CONFIG_METADATA_KEY}.{CONFIG_REPORTS_KEY}.",
            )
        )
        return None if has_invalid_structure else reports_values

    @staticmethod
    def _mapping_or_cause(value: object, path: str, causes: list[str]) -> Mapping[str, object]:
        """Return `value` as a mapping; None is an empty mapping and anything else a cause."""
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        causes.append(f"'{path}' debe ser un mapeo de claves y valores")
        return {}

    @staticmethod
    def _unknown_key_causes(
        section: Mapping[str, object], known_keys: tuple[str, ...], prefix: str
    ) -> list[str]:
        """Return one cause per key of `section` that is not in `known_keys`."""
        return [
            f"Clave no reconocida en config.yml: '{prefix}{key}'"
            for key in section
            if key not in known_keys
        ]

    def _build_mongo_settings(self, causes: list[str]) -> MongoSettings | None:
        """Validate the MongoDB values of the environment; the cause names the field only."""
        values = {
            "host": self._environment.get(MONGO_HOST_VARIABLE, ""),
            "port": self._environment.get(MONGO_PORT_VARIABLE, ""),
            "username": self._environment.get(MONGO_USERNAME_VARIABLE, ""),
            "password": self._environment.get(MONGO_PASSWORD_VARIABLE, ""),
            "database": self._environment.get(MONGO_DATABASE_VARIABLE, ""),
            "auth_source": (
                self._environment.get(MONGO_AUTH_SOURCE_VARIABLE) or DEFAULT_MONGO_AUTH_SOURCE
            ),
        }
        try:
            return MongoSettings.model_validate(values)
        except ValidationError as error:
            causes.extend(
                f"MongoDB: '{'.'.join(str(part) for part in detail['loc'])}' "
                f"{self._describe(detail['type'])}"
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
