from datetime import datetime

from interface_sync.constants.enums import InterfaceStatus, LogEvent
from interface_sync.persistence import InterfaceChanges, InterfaceModification
from interface_sync.synchronization import ChangeReporter
from interface_sync.utils.logger import ServiceLogger


def test_updated_fields_are_logged_with_previous_and_new_values(
    recording_logger: ServiceLogger, now: datetime
):
    """RF-014: an updated interface logs its scan_url and the previous and new value per field."""
    changes = InterfaceChanges(
        modifications=[
            InterfaceModification(
                scan_url="http://scan/1.log",
                updated_at=now,
                field_changes={"name": ("OLD", "NEW"), "capacity_gbps": (10.0, 40.0)},
            )
        ]
    )

    ChangeReporter(recording_logger).report(changes)

    assert recording_logger.records == [
        (
            "info",
            LogEvent.INTERFACE_UPDATED,
            "http://scan/1.log | name: OLD -> NEW, capacity_gbps: 10.0 -> 40.0",
        )
    ]


def test_status_change_is_logged_with_previous_and_new_status(
    recording_logger: ServiceLogger, now: datetime
):
    """RF-014: a status change logs the scan_url and both statuses."""
    changes = InterfaceChanges(
        modifications=[
            InterfaceModification(
                scan_url="http://scan/1.log",
                updated_at=now,
                status_change=(InterfaceStatus.ACTIVE, InterfaceStatus.DECOMMISSIONED),
            )
        ]
    )

    ChangeReporter(recording_logger).report(changes)

    assert recording_logger.records == [
        ("info", LogEvent.STATUS_CHANGED, "http://scan/1.log | activa -> desincorporada")
    ]


def test_reactivation_with_data_logs_both_events(recording_logger: ServiceLogger, now: datetime):
    """RF-014: one modification with data and status writes one line for each."""
    changes = InterfaceChanges(
        modifications=[
            InterfaceModification(
                scan_url="u",
                updated_at=now,
                field_changes={"name": ("A", "B")},
                status_change=(InterfaceStatus.DECOMMISSIONED, InterfaceStatus.ACTIVE),
            )
        ]
    )

    ChangeReporter(recording_logger).report(changes)

    assert [message for _, message, _ in recording_logger.records] == [
        LogEvent.INTERFACE_UPDATED,
        LogEvent.STATUS_CHANGED,
    ]


def test_registrations_and_unchanged_interfaces_log_nothing(
    recording_logger: ServiceLogger, make_document
):
    """Only modifications are reported per interface; registrations go in the page summary."""
    changes = InterfaceChanges(registrations=[make_document()], unchanged_count=5)

    ChangeReporter(recording_logger).report(changes)

    assert recording_logger.records == []
