from traffic_collector.constants.enums import FailureCause


class ScanError(Exception):
    """A failed download from SCAN. `cause` is the reason reported for the interface [RF-022]."""

    cause: FailureCause

    def __str__(self) -> str:
        """Return the cause text."""
        return self.cause.value


class ScanTimeout(ScanError):
    """SCAN did not answer within the configured time."""

    cause = FailureCause.TIMEOUT


class ScanUnreachable(ScanError):
    """The connection to SCAN could not be established."""

    cause = FailureCause.UNREACHABLE


class ScanUnauthorized(ScanError):
    """SCAN rejected the credentials (HTTP 401)."""

    cause = FailureCause.UNAUTHORIZED


class ScanHttpError(ScanError):
    """SCAN answered with an HTTP status of 400 or higher, other than 401."""

    cause = FailureCause.HTTP_ERROR

    def __init__(self, status_code: int) -> None:
        """Keep the HTTP status that SCAN answered."""
        super().__init__(status_code)
        self.status_code = status_code

    def __str__(self) -> str:
        """Return the cause text with the HTTP status."""
        return f"{self.cause.value} (HTTP {self.status_code})"


class ScanEmptyResponse(ScanError):
    """SCAN answered successfully but the body has no data."""

    cause = FailureCause.EMPTY_RESPONSE
