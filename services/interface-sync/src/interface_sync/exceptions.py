from interface_sync.constants.constants import DATABASE_ERROR_CAUSE


class InvalidConfigError(Exception):
    """Raised when `config.yml` is invalid. Holds every cause that was detected."""

    def __init__(self, causes: list[str]) -> None:
        """Store the causes and build a summary message from them."""
        self.causes = causes
        super().__init__("; ".join(causes))


class ServiceStartupError(Exception):
    """Base error of a condition that prevents the whole process from starting."""


class MissingCredentialsError(ServiceStartupError):
    """Raised when the SCAN credentials are not available in the environment."""


class MissingDatabaseSettingsError(ServiceStartupError):
    """Raised when the database settings are not available in the environment."""


class ScanUnavailableError(ServiceStartupError):
    """Raised when one or more SCAN base URLs do not answer at startup."""


class DatabaseUnavailableError(ServiceStartupError):
    """Raised when the database does not answer at startup."""


class DatabaseError(Exception):
    """Raised when a database operation fails; `cause` feeds log and terminal."""

    def __init__(self, cause: str = DATABASE_ERROR_CAUSE) -> None:
        """Store the cause and use it as the error message."""
        self.cause = cause
        super().__init__(cause)


class MissingLayerError(Exception):
    """Raised when an interface reaches the synchronization without its layer."""


class EmptyListingError(Exception):
    """Raised when a decommission is requested without any interface present in the listing."""


class PageFetchError(Exception):
    """Base error of a SCAN page that could not be obtained; `cause` feeds log and terminal."""

    def __init__(self, cause: str) -> None:
        """Store the cause and use it as the error message."""
        self.cause = cause
        super().__init__(cause)


class ScanTimeoutError(PageFetchError):
    """Raised when SCAN does not answer within the allowed time."""

    def __init__(self) -> None:
        """Set the fixed cause."""
        super().__init__("tiempo de espera agotado")


class ScanConnectionError(PageFetchError):
    """Raised when SCAN cannot be reached."""

    def __init__(self) -> None:
        """Set the fixed cause."""
        super().__init__("sin conexión a SCAN")


class ScanUnauthorizedError(PageFetchError):
    """Raised when SCAN answers HTTP 401."""

    def __init__(self) -> None:
        """Set the fixed cause."""
        super().__init__("credenciales rechazadas")


class ScanHttpError(PageFetchError):
    """Raised when SCAN answers an HTTP status of 400 or higher, except 401."""

    def __init__(self, status_code: int) -> None:
        """Keep the status code and build the cause from it."""
        self.status_code = status_code
        super().__init__(f"error de SCAN (HTTP {status_code})")


class UnreadablePageError(PageFetchError):
    """Raised when the expected HTML structure is not present in the page."""

    def __init__(self, missing_element: str) -> None:
        """Build the cause from the element that was not found."""
        super().__init__(f"página ilegible ({missing_element} ausente)")


class InvalidListingError(PageFetchError):
    """Raised when a page listing has no complete interface to continue the process."""

    def __init__(self, reason: str) -> None:
        """Build the cause from the reason why the listing is invalid."""
        super().__init__(f"listado inválido ({reason})")


class UnsupportedPageError(PageFetchError):
    """Raised when there is no parser for the layer and vendor of the page."""

    def __init__(self, layer: str, vendor: str) -> None:
        """Build the cause from the unsupported layer and vendor."""
        super().__init__(f"sin soporte para la capa '{layer}' y el proveedor '{vendor}'")
