from collections.abc import Callable

import pytest

from interface_sync.constants.enums import InterfaceStatus, LogEvent
from interface_sync.exceptions import DatabaseError, EmptyListingError
from interface_sync.models import PageResult
from interface_sync.persistence import InterfaceChanges, InterfaceDocument, InterfaceRepository
from interface_sync.synchronization import (
    ChangeReporter,
    InterfaceChangePlanner,
    LayerDecommissioner,
)
from interface_sync.utils.logger import ServiceLogger

Document = Callable[..., InterfaceDocument]


class FakeRepository:
    """In-memory repository double: records applied changes and can fail on demand."""

    def __init__(self, active_by_layer: dict[str, list[InterfaceDocument]] | None = None) -> None:
        self.active_by_layer = active_by_layer or {}
        self.applied: list[InterfaceChanges] = []
        self.queried_layers: list[str] = []
        self.failing_layers: set[str] = set()
        self.fail_on_apply = False

    def find_active_by_layer(self, layer: str) -> list[InterfaceDocument]:
        self.queried_layers.append(layer)
        if layer in self.failing_layers:
            raise DatabaseError()
        return self.active_by_layer.get(layer, [])

    def apply(self, changes: InterfaceChanges) -> None:
        if self.fail_on_apply:
            raise DatabaseError()
        self.applied.append(changes)


def build_decommissioner(repository: FakeRepository, logger: ServiceLogger) -> LayerDecommissioner:
    return LayerDecommissioner(
        repository,  # type: ignore[arg-type]
        InterfaceChangePlanner(),
        ChangeReporter(logger),
        logger,
    )


def succeeded(label: str, layer: str, *scan_urls: str) -> PageResult:
    return PageResult(page_label=label, layer=layer, present_scan_urls=frozenset(scan_urls))


def test_missing_interfaces_of_a_successful_layer_are_decommissioned(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-009: active interfaces absent from the layer listing are decommissioned."""
    repository = FakeRepository(
        {
            "BORDE": [
                make_document(scan_url="http://scan/stays.log"),
                make_document(scan_url="http://scan/gone.log"),
            ]
        }
    )
    decommissioner = build_decommissioner(repository, recording_logger)

    [result] = decommissioner.decommission(
        [succeeded("BORDE HUAWEI", "BORDE", "http://scan/stays.log")]
    )

    assert result.succeeded
    assert result.decommissioned_count == 1
    [applied] = repository.applied
    assert [modification.scan_url for modification in applied.modifications] == [
        "http://scan/gone.log"
    ]
    assert ("info", LogEvent.LAYER_SUMMARY, "BORDE | desincorporadas: 1 | sin cambios: 1") in (
        recording_logger.records
    )
    assert LogEvent.STATUS_CHANGED in recording_logger.messages("info")


def test_present_urls_are_the_union_of_every_page_of_the_layer(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-009: an interface listed by the sibling page of the layer is not decommissioned."""
    repository = FakeRepository(
        {
            "BORDE": [
                make_document(scan_url="http://scan/huawei.log"),
                make_document(scan_url="http://scan/juniper.log"),
                make_document(scan_url="http://scan/gone.log"),
            ]
        }
    )
    decommissioner = build_decommissioner(repository, recording_logger)

    [result] = decommissioner.decommission(
        [
            succeeded("BORDE HUAWEI", "BORDE", "http://scan/huawei.log"),
            succeeded("BORDE JUNIPER", "BORDE", "http://scan/juniper.log"),
        ]
    )

    assert result.decommissioned_count == 1
    assert repository.applied[0].modifications[0].scan_url == "http://scan/gone.log"


def test_layer_with_a_scraping_failure_is_skipped_untouched(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-010: a failed page may be hiding interfaces, so its layer is not evaluated."""
    repository = FakeRepository({"BORDE": [make_document()]})
    decommissioner = build_decommissioner(repository, recording_logger)

    [result] = decommissioner.decommission(
        [
            succeeded("BORDE HUAWEI", "BORDE", "http://scan/other.log"),
            PageResult(page_label="BORDE JUNIPER", layer="BORDE", cause="tiempo de espera agotado"),
        ]
    )

    assert result.skipped_reason == "páginas fallidas: BORDE JUNIPER"
    assert result.decommissioned_count == 0
    assert repository.queried_layers == []
    assert repository.applied == []
    assert recording_logger.records[0][:2] == ("warning", LogEvent.LAYER_SKIPPED)


def test_layer_with_a_database_failure_page_is_skipped(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-010: a page whose storage failed also blocks the decommission of its layer."""
    repository = FakeRepository({"BORDE": [make_document()]})
    decommissioner = build_decommissioner(repository, recording_logger)

    [result] = decommissioner.decommission(
        [
            PageResult(
                page_label="BORDE HUAWEI", layer="BORDE", database_cause="error de base de datos"
            )
        ]
    )

    assert result.skipped_reason is not None
    assert repository.applied == []


def test_failed_layer_does_not_block_other_layers(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-010: layers are independent; one failing never stops the rest."""
    repository = FakeRepository(
        {"DIST": [make_document(layer="DIST", scan_url="http://scan/gone.log")]}
    )
    decommissioner = build_decommissioner(repository, recording_logger)

    results = decommissioner.decommission(
        [
            PageResult(page_label="BORDE HUAWEI", layer="BORDE", cause="sin conexión a SCAN"),
            succeeded("DIST HUAWEI", "DIST", "http://scan/other.log"),
        ]
    )

    assert [result.layer for result in results] == ["BORDE", "DIST"]
    assert results[0].skipped_reason is not None
    assert results[1].decommissioned_count == 1


def test_database_error_while_querying_fails_the_layer(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-010: a database error is reported for the layer, with the database named in the log."""
    repository = FakeRepository({"BORDE": [make_document()]})
    repository.failing_layers.add("BORDE")
    decommissioner = build_decommissioner(repository, recording_logger)

    [result] = decommissioner.decommission(
        [succeeded("BORDE HUAWEI", "BORDE", "http://scan/x.log")]
    )

    assert not result.succeeded
    assert result.database_cause == "error de base de datos"
    assert repository.applied == []
    assert recording_logger.records == [
        ("error", LogEvent.DATABASE_FAILED, "BORDE | desincorporación | error de base de datos")
    ]


def test_database_error_while_writing_fails_the_layer_without_summary(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-010: if the write fails nothing is logged as applied."""
    repository = FakeRepository({"BORDE": [make_document()]})
    repository.fail_on_apply = True
    decommissioner = build_decommissioner(repository, recording_logger)

    [result] = decommissioner.decommission(
        [succeeded("BORDE HUAWEI", "BORDE", "http://scan/x.log")]
    )

    assert not result.succeeded
    assert recording_logger.messages("info") == []
    assert recording_logger.messages("error") == [LogEvent.DATABASE_FAILED]


def test_database_failure_in_one_layer_still_decommissions_the_next(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-010: what is applied in a healthy layer is kept after another layer fails."""
    repository = FakeRepository(
        {"DIST": [make_document(layer="DIST", scan_url="http://scan/gone.log")]}
    )
    repository.failing_layers.add("BORDE")
    decommissioner = build_decommissioner(repository, recording_logger)

    results = decommissioner.decommission(
        [
            succeeded("BORDE HUAWEI", "BORDE", "http://scan/x.log"),
            succeeded("DIST HUAWEI", "DIST", "http://scan/y.log"),
        ]
    )

    assert not results[0].succeeded
    assert results[1].succeeded
    assert results[1].decommissioned_count == 1


def test_nothing_missing_means_nothing_decommissioned(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-011: when every active interface is still listed, no modification is written."""
    repository = FakeRepository({"BORDE": [make_document(scan_url="http://scan/a.log")]})
    decommissioner = build_decommissioner(repository, recording_logger)

    [result] = decommissioner.decommission(
        [succeeded("BORDE HUAWEI", "BORDE", "http://scan/a.log")]
    )

    assert result.decommissioned_count == 0
    assert repository.applied[0].modifications == []


def test_already_decommissioned_interfaces_are_not_queried_or_touched(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-009: the layer query only brings active interfaces, so decommissioned ones stay as is."""
    repository = FakeRepository(
        {
            "BORDE": [
                make_document(scan_url="http://scan/old.log", status=InterfaceStatus.DECOMMISSIONED)
            ]
        }
    )
    decommissioner = build_decommissioner(repository, recording_logger)

    decommissioner.decommission([succeeded("BORDE HUAWEI", "BORDE", "http://scan/a.log")])

    assert repository.queried_layers == ["BORDE"]


def test_successful_page_without_present_urls_never_decommissions(
    recording_logger: ServiceLogger, make_document: Document
):
    """RF-006/RF-009: an empty listing must not wipe a layer; the guard refuses it loudly."""
    repository = FakeRepository({"BORDE": [make_document()]})
    decommissioner = build_decommissioner(repository, recording_logger)

    with pytest.raises(EmptyListingError):
        decommissioner.decommission([succeeded("BORDE HUAWEI", "BORDE")])

    assert repository.applied == []


def test_results_follow_the_order_in_which_layers_first_appear(
    recording_logger: ServiceLogger,
):
    """The result list keeps the order of the pages in config.yml."""
    repository = FakeRepository()
    decommissioner = build_decommissioner(repository, recording_logger)

    results = decommissioner.decommission(
        [
            succeeded("BRAS", "BRAS", "u1"),
            succeeded("BORDE HUAWEI", "BORDE", "u2"),
            succeeded("BORDE JUNIPER", "BORDE", "u3"),
        ]
    )

    assert [result.layer for result in results] == ["BRAS", "BORDE"]


def test_fake_repository_matches_the_real_repository_interface():
    """Guards the double: the methods it fakes exist in the real repository."""
    for method in ("find_active_by_layer", "apply"):
        assert callable(getattr(InterfaceRepository, method))
