from interface_sync.constants.enums import LogEvent
from interface_sync.persistence import InterfaceChanges
from interface_sync.utils.logger import ServiceLogger


class ChangeReporter:
    """Writes to the log the changes that were applied to stored interfaces [RF-014]."""

    def __init__(self, logger: ServiceLogger) -> None:
        """Set the logger that records the changes."""
        self._logger = logger

    def report(self, changes: InterfaceChanges) -> None:
        """Log every updated data field and every status change of the applied modifications."""
        for modification in changes.modifications:
            if modification.field_changes:
                differences = ", ".join(
                    f"{field}: {previous} -> {new}"
                    for field, (previous, new) in modification.field_changes.items()
                )
                self._logger.info(
                    LogEvent.INTERFACE_UPDATED, f"{modification.scan_url} | {differences}"
                )
            if modification.status_change is not None:
                previous_status, new_status = modification.status_change
                self._logger.info(
                    LogEvent.STATUS_CHANGED,
                    f"{modification.scan_url} | {previous_status} -> {new_status}",
                )
