import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from reports.constants.constants import (
    ALLOWED_STRFTIME_DIRECTIVES,
    CONFIG_DATE_FORMAT_KEY,
    CONFIG_EXPORT_PATH_KEY,
    CONFIG_PREFIX_NAME_KEY,
    DEFAULT_DATE_FORMAT,
    DEFAULT_EXPORT_PATH,
    DEFAULT_PREFIX_NAME,
    FORBIDDEN_FILE_NAME_CHARACTERS,
    SAMPLE_MOMENT,
    STRFTIME_DIRECTIVE_MARK,
)


@dataclass(frozen=True, slots=True)
class ReportConfig:
    """Validated values of `metadata.reports` in `config.yml` [RF-032]."""

    prefix_name: str
    date_format: str
    export_path: Path


class ReportConfigValidator:
    """Validates the `metadata.reports` section and applies the defaults of the omitted keys.

    Every invalid value is recorded as a cause instead of stopping at the first one. The
    export directory is never created: it must already exist and be writable.
    """

    def validate(self, section: Mapping[str, object], causes: list[str]) -> ReportConfig | None:
        """Return the config, or None after recording one cause per invalid key."""
        initial_cause_count = len(causes)
        prefix_name = section.get(CONFIG_PREFIX_NAME_KEY, DEFAULT_PREFIX_NAME)
        date_format = section.get(CONFIG_DATE_FORMAT_KEY, DEFAULT_DATE_FORMAT)
        export_path = section.get(CONFIG_EXPORT_PATH_KEY, DEFAULT_EXPORT_PATH)
        causes.extend(self._prefix_name_causes(prefix_name))
        causes.extend(self._date_format_causes(date_format))
        causes.extend(self._export_path_causes(export_path))
        if len(causes) > initial_cause_count:
            return None
        return ReportConfig(
            prefix_name=str(prefix_name),
            date_format=str(date_format),
            export_path=Path(str(export_path)).expanduser(),
        )

    @staticmethod
    def contains_forbidden_characters(text: str) -> bool:
        """Return True if `text` has a character that a file name cannot contain."""
        return any(character in FORBIDDEN_FILE_NAME_CHARACTERS for character in text)

    def _prefix_name_causes(self, value: object) -> list[str]:
        """Return the causes that make `prefix_name` invalid."""
        key = CONFIG_PREFIX_NAME_KEY
        if not isinstance(value, str):
            return [f"'{key}' debe ser texto"]
        if not value.strip():
            return [f"'{key}' no puede estar vacío"]
        if self.contains_forbidden_characters(value):
            return [f"'{key}' contiene caracteres no permitidos en un nombre de archivo"]
        return []

    def _date_format_causes(self, value: object) -> list[str]:
        """Return the causes that make `date_format` invalid.

        `strftime` leaves unknown directives as literal text on Linux, so each `%x` is checked
        against the standard directives and a sample date is formatted to detect forbidden
        characters in the result (for example `%x` produces `11/11/26`).
        """
        key = CONFIG_DATE_FORMAT_KEY
        if not isinstance(value, str):
            return [f"'{key}' debe ser texto"]
        if not value:
            return [f"'{key}' no puede estar vacío"]
        directive_causes = self._directive_causes(value)
        if directive_causes:
            return directive_causes
        try:
            sample = SAMPLE_MOMENT.strftime(value)
        except ValueError:
            return [f"'{key}' no es un formato de fecha válido"]
        if self.contains_forbidden_characters(sample):
            return [f"'{key}' produce caracteres no permitidos en un nombre de archivo"]
        return []

    @staticmethod
    def _directive_causes(date_format: str) -> list[str]:
        """Return the causes found in the `%` directives of `date_format`."""
        key = CONFIG_DATE_FORMAT_KEY
        position = 0
        while position < len(date_format):
            if date_format[position] != STRFTIME_DIRECTIVE_MARK:
                position += 1
                continue
            if position + 1 == len(date_format):
                return [f"'{key}' termina con un '%' sin directiva"]
            directive = date_format[position + 1]
            if directive not in ALLOWED_STRFTIME_DIRECTIVES:
                return [f"'{key}' usa la directiva no admitida '%{directive}'"]
            position += 2
        return []

    @staticmethod
    def _export_path_causes(value: object) -> list[str]:
        """Return the causes that make `export_path` invalid."""
        key = CONFIG_EXPORT_PATH_KEY
        if not isinstance(value, str):
            return [f"'{key}' debe ser texto"]
        if not value.strip():
            return [f"'{key}' no puede estar vacío"]
        directory = Path(value).expanduser()
        if not directory.is_dir():
            return [f"'{key}' no es un directorio existente: {directory}"]
        if not os.access(directory, os.W_OK | os.X_OK):
            return [f"'{key}' no tiene permiso de escritura: {directory}"]
        return []
