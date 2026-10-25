from collections.abc import Callable
from datetime import datetime

import pytest
from pydantic import ValidationError

from interface_sync.constants.enums import InterfaceStatus
from interface_sync.persistence import InterfaceChanges, InterfaceDocument, InterfaceModification

Document = Callable[..., InterfaceDocument]


def test_document_requires_a_valid_status(make_document: Document):
    """The status is a validated Enum: values outside activa/desincorporada are refused."""
    with pytest.raises(ValidationError):
        make_document(status="inactiva")


def test_document_accepts_status_values_as_text(make_document: Document):
    """The stored text values map back to the Enum."""
    assert make_document(status="desincorporada").status is InterfaceStatus.DECOMMISSIONED
    assert make_document(status="activa").status is InterfaceStatus.ACTIVE


def test_document_capacity_is_always_a_float(make_document: Document):
    """An integer capacity is coerced so the field never mixes int and float."""
    capacity = make_document(capacity_gbps=40).capacity_gbps

    assert isinstance(capacity, float)
    assert capacity == 40.0


@pytest.mark.parametrize("missing", ["layer", "name", "vendor", "scan_url"])
def test_document_requires_every_text_field(make_document: Document, missing: str):
    """Required fields cannot be left out."""
    with pytest.raises(ValidationError):
        InterfaceDocument.model_validate(make_document().model_dump(exclude={"id", missing}))


def test_document_rejects_non_date_timestamps(make_document: Document):
    """Dates must be real datetimes."""
    with pytest.raises(ValidationError):
        make_document(created_at="not a date")


def test_document_has_no_id_until_stored(make_document: Document):
    """The internal _id is empty for a document that was not stored yet."""
    assert make_document().id is None


def test_modification_classifies_data_only_change(now: datetime):
    """A modification with fields and no status is an update."""
    modification = InterfaceModification(
        scan_url="u", updated_at=now, field_changes={"name": ("a", "b")}
    )

    assert modification.changes_data
    assert not modification.is_decommission
    assert not modification.is_reactivation


def test_modification_classifies_decommission(now: datetime):
    """ACTIVE to DECOMMISSIONED is a decommission."""
    modification = InterfaceModification(
        scan_url="u",
        updated_at=now,
        status_change=(InterfaceStatus.ACTIVE, InterfaceStatus.DECOMMISSIONED),
    )

    assert modification.is_decommission
    assert not modification.is_reactivation
    assert not modification.changes_data


def test_modification_classifies_reactivation(now: datetime):
    """DECOMMISSIONED to ACTIVE is a reactivation."""
    modification = InterfaceModification(
        scan_url="u",
        updated_at=now,
        status_change=(InterfaceStatus.DECOMMISSIONED, InterfaceStatus.ACTIVE),
    )

    assert modification.is_reactivation
    assert not modification.is_decommission


def test_changes_counters_split_updates_decommissions_and_reactivations(now: datetime):
    """The summary counters classify each modification."""
    changes = InterfaceChanges(
        modifications=[
            InterfaceModification(scan_url="1", updated_at=now, field_changes={"name": ("a", "b")}),
            InterfaceModification(
                scan_url="2",
                updated_at=now,
                field_changes={"name": ("a", "b")},
                status_change=(InterfaceStatus.DECOMMISSIONED, InterfaceStatus.ACTIVE),
            ),
            InterfaceModification(
                scan_url="3",
                updated_at=now,
                status_change=(InterfaceStatus.ACTIVE, InterfaceStatus.DECOMMISSIONED),
            ),
        ],
        unchanged_count=4,
    )

    assert changes.updated_count == 2
    assert changes.reactivated_count == 1
    assert changes.decommissioned_count == 1


def test_empty_changes_have_zero_counters():
    """No changes means every counter is 0."""
    changes = InterfaceChanges()

    assert (changes.updated_count, changes.reactivated_count, changes.decommissioned_count) == (
        0,
        0,
        0,
    )
