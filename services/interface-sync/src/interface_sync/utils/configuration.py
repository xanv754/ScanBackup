from pathlib import Path
from typing import ClassVar

import yaml
from pydantic import ValidationError
from pydantic_core import ErrorDetails

from interface_sync.exceptions import InvalidConfigError
from interface_sync.models import PageConfig
from interface_sync.utils.logger import ServiceLogger


class ConfigurationFile:
    """Reads, validates and standardizes the SCAN listing pages declared in `config.yml`.

    Expected structure: a `links` list of `{layer, url, vendor?}` entries. Nothing else
    is valid. A missing, unreadable, non-YAML or empty file stops the inspection at once;
    any other problem is accumulated so that every cause is reported in a single run.
    """

    LINKS_KEY = "links"
    ERROR_MESSAGES: ClassVar[dict[str, str]] = {
        "missing": "campo obligatorio ausente",
        "string_too_short": "campo obligatorio vacío",
        "extra_forbidden": "clave no reconocida",
        "string_type": "debe ser texto",
    }

    def __init__(self, config_path: Path, logger: ServiceLogger) -> None:
        """Set the file to read and the logger that records every invalid cause."""
        self._config_path = config_path
        self._logger = logger

    def load(self) -> list[PageConfig]:
        """Return the standardized pages, or raise `InvalidConfigError` after logging each cause."""
        try:
            pages = self._build_pages()
        except InvalidConfigError as error:
            for cause in error.causes:
                self._logger.error("Configuración inválida", cause)
            raise
        self._logger.info("Configuración cargada", f"{len(pages)} páginas")
        return pages

    def _build_pages(self) -> list[PageConfig]:
        """Validate every entry of the file and raise with all the causes found."""
        raw_links, causes = self._extract_links(self._read_content())
        if raw_links is None:
            raise InvalidConfigError(causes)

        pages: list[tuple[int, PageConfig]] = []
        for position, raw_link in enumerate(raw_links, start=1):
            try:
                pages.append((position, PageConfig.model_validate(raw_link)))
            except ValidationError as error:
                causes.extend(self._describe_errors(position, error))
        causes.extend(self._find_duplicates(pages))

        if causes:
            raise InvalidConfigError(causes)
        return [page for _, page in pages]

    def _read_content(self) -> dict:
        """Parse the file; raise `InvalidConfigError` when it cannot be inspected further."""
        try:
            raw_text = self._config_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise InvalidConfigError(
                [f"No se puede leer el archivo {self._config_path} ({error})"]
            ) from error
        try:
            content = yaml.safe_load(raw_text)
        except yaml.YAMLError as error:
            reason = " ".join(str(error).split())
            raise InvalidConfigError(
                [f"El archivo {self._config_path} no es YAML válido ({reason})"]
            ) from error
        if not content:
            raise InvalidConfigError(
                [f"El archivo {self._config_path} no tiene contenido"]
            )
        if not isinstance(content, dict):
            raise InvalidConfigError(
                [
                    f"El archivo {self._config_path} debe ser un mapeo con '{self.LINKS_KEY}'"
                ]
            )
        return content

    def _extract_links(self, content: dict) -> tuple[list | None, list[str]]:
        """Return the raw `links` entries (None if not inspectable) and the causes found."""
        causes = [
            f"Clave no reconocida en la raíz: '{key}'"
            for key in content
            if key != self.LINKS_KEY
        ]
        raw_links = content.get(self.LINKS_KEY)
        if not raw_links:
            causes.append(f"La clave '{self.LINKS_KEY}' no existe o está vacía")
            return None, causes
        if not isinstance(raw_links, list):
            causes.append(f"La clave '{self.LINKS_KEY}' debe ser una lista")
            return None, causes
        return raw_links, causes

    def _describe_errors(self, position: int, error: ValidationError) -> list[str]:
        """Translate the validation errors of one entry into readable causes."""
        return [
            f"Página {position}: {self._describe_field(detail)}: {self._describe_reason(detail)}"
            for detail in error.errors()
        ]

    @staticmethod
    def _describe_field(detail: ErrorDetails) -> str:
        """Name the field that failed, or the entry itself when it is not a mapping."""
        return ".".join(str(part) for part in detail["loc"]) or "entrada"

    def _describe_reason(self, detail: ErrorDetails) -> str:
        """Return the cause text for a validation error."""
        if detail["type"] == "value_error":
            return str(detail["ctx"]["error"])  # type: ignore
        if detail["type"] == "model_type":
            return "cada entrada debe ser un mapeo con layer, url y vendor opcional"
        return self.ERROR_MESSAGES.get(detail["type"], detail["msg"])

    @staticmethod
    def _find_duplicates(pages: list[tuple[int, PageConfig]]) -> list[str]:
        """Report pages that share the same standardized layer and vendor, by file position."""
        first_seen: dict[tuple[str, str], int] = {}
        causes: list[str] = []
        for position, page in pages:
            key = (page.layer, page.vendor)
            if key in first_seen:
                causes.append(
                    f"Capa '{page.layer}' y proveedor '{page.vendor}' repetidos "
                    f"entre las páginas {first_seen[key]} y {position}"
                )
            else:
                first_seen[key] = position
        return causes
