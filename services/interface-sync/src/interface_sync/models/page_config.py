from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

from interface_sync.constants.constants import ALLOWED_URL_SCHEMES, UNDEFINED_VENDOR


class PageConfig(BaseModel):
    """A SCAN listing page declared in `config.yml`, already validated and standardized.

    Whitespace is stripped from every text field. `layer` and `vendor` are capitalized
    (first letter in uppercase, the rest in lowercase). A missing, empty or `undefined`
    vendor becomes `Undefined`. The URL keeps its original casing.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    layer: str = Field(min_length=1)
    url: str = Field(min_length=1)
    vendor: str = UNDEFINED_VENDOR

    @property
    def label(self) -> str:
        """Return the layer and vendor as a short text for logs and terminal."""
        return f"{self.layer} {self.vendor}"

    @field_validator("vendor", mode="before")
    @classmethod
    def _default_missing_vendor(cls, vendor: str | None) -> str:
        """Replace an empty YAML value (`vendor:`) with the undefined vendor."""
        return UNDEFINED_VENDOR if vendor is None else vendor

    @field_validator("layer")
    @classmethod
    def _standardize_layer(cls, layer: str) -> str:
        """Capitalize the layer name."""
        return layer.capitalize()

    @field_validator("vendor")
    @classmethod
    def _standardize_vendor(cls, vendor: str) -> str:
        """Capitalize the vendor name; an empty vendor becomes `Undefined`."""
        return vendor.capitalize() or UNDEFINED_VENDOR

    @field_validator("url")
    @classmethod
    def _validate_url(cls, url: str) -> str:
        """Require an `http` or `https` scheme and a host."""
        try:
            parsed_url = urlsplit(url)
            host = parsed_url.hostname
        except ValueError as error:
            raise ValueError(f"URL malformada ({error})") from error
        if parsed_url.scheme.lower() not in ALLOWED_URL_SCHEMES:
            raise ValueError("la URL debe usar el esquema http o https")
        if not host:
            raise ValueError("la URL no tiene host")
        return url
