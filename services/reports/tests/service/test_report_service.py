from datetime import date, datetime
from pathlib import Path

import pytest

from reports.constants.constants import CARACAS_TIMEZONE
from reports.constants.enums import ExitCode
from reports.domain.date_range import DateRange
from reports.domain.period_calculator import PeriodCalculator
from reports.exceptions import ProcessError
from reports.export import ReportFileNamer
from reports.report_config import ReportConfig
from reports.reporting import (
    ExportFailed,
    FileGenerated,
    LayerFinished,
    MissingDay,
    RunFinished,
    RunStarted,
)
from reports.service import LayerProcessor, ReportService
from tests.fakes import (
    FakeDailySummaryRepository,
    FakeExporter,
    FakeInterfaceRepository,
    FixedClock,
    RecordingSink,
)
from tests.service.builders import make_interface, make_summary

RANGE = DateRange(start=date(2026, 3, 1), end=date(2026, 3, 3))
GENERATED_AT = datetime(2026, 11, 10, 15, 30, 0, tzinfo=CARACAS_TIMEZONE)
EXPORT_DIRECTORY = Path("/exports")


def build_service(
    interface_repository: FakeInterfaceRepository,
    summary_repository: FakeDailySummaryRepository,
    exporter: FakeExporter | None = None,
) -> tuple[ReportService, FakeExporter, RecordingSink]:
    """Wire the service with fakes and return it with the exporter and the sink."""
    exporter = exporter or FakeExporter()
    sink = RecordingSink()
    layer_processor = LayerProcessor(
        interface_repository, summary_repository, PeriodCalculator(), exporter, sink
    )
    config = ReportConfig("ScanBackup", "%Y%m%d_%H%M%S", EXPORT_DIRECTORY)
    service = ReportService(
        interface_repository,
        layer_processor,
        exporter,
        ReportFileNamer(config),
        EXPORT_DIRECTORY,
        FixedClock(GENERATED_AT),
        sink,
    )
    return service, exporter, sink


def layers_with_data(
    *layer_names: str,
) -> tuple[FakeInterfaceRepository, FakeDailySummaryRepository]:
    """Build repositories where every given layer has one interface with all the days."""
    interfaces = {name: [make_interface(f"if-{name}")] for name in layer_names}
    summaries = [
        make_summary(interface) for group in interfaces.values() for interface in group
    ]
    days = {
        interface.id: set(RANGE.day_keys())
        for group in interfaces.values()
        for interface in group
    }
    return FakeInterfaceRepository(interfaces), FakeDailySummaryRepository(
        summaries, days
    )


def test_rf044_everything_succeeds_gives_exit_code_zero() -> None:
    """RF-044: all layers succeed, one has data and the file is written: exit code 0."""
    service, exporter, sink = build_service(*layers_with_data("BORDE", "BRAS"))
    result = service.run(RANGE)
    assert result.exit_code == ExitCode.SUCCESS
    assert exporter.saved_paths == [
        EXPORT_DIRECTORY / "ScanBackup_20261110_153000.fake"
    ]
    assert result.export_summary is not None
    assert (
        result.export_summary.sheet_count,
        result.export_summary.interface_count,
    ) == (2, 2)
    assert sink.of_type(FileGenerated)[0].summary == result.export_summary
    assert sink.of_type(RunFinished)[0].result == result


def test_rf045_run_start_is_published_once_with_the_range() -> None:
    """RF-045: the start of the run carries the requested range."""
    service, _, sink = build_service(*layers_with_data("BORDE"))
    service.run(RANGE)
    assert [event.date_range for event in sink.of_type(RunStarted)] == [RANGE]


def test_rf039_sheets_follow_the_layer_order() -> None:
    """RF-039: fixed layers first in their order, then the others alphabetically."""
    service, exporter, _ = build_service(
        *layers_with_data("ZETA", "IXP", "ALFA", "BORDE", "BRAS")
    )
    service.run(RANGE)
    assert [layer.layer for layer in exporter.layers] == [
        "BORDE",
        "BRAS",
        "IXP",
        "ALFA",
        "ZETA",
    ]


def test_rf034_layers_are_processed_one_by_one_in_order() -> None:
    """RF-034: a layer is finished before the next one starts."""
    service, _, sink = build_service(*layers_with_data("IXP", "BORDE"))
    service.run(RANGE)
    assert [event.result.layer for event in sink.of_type(LayerFinished)] == [
        "BORDE",
        "IXP",
    ]


def test_rf034_layer_names_with_different_case_are_one_layer() -> None:
    """RF-034: `borde` and `BORDE` are the same layer, named in uppercase."""
    first, second = make_interface("a"), make_interface("b")
    interface_repository = FakeInterfaceRepository(
        {"BORDE": [first], "borde": [second]}
    )
    summary_repository = FakeDailySummaryRepository(
        [make_summary(first), make_summary(second)]
    )
    service, exporter, _ = build_service(interface_repository, summary_repository)
    service.run(RANGE)
    assert [layer.layer for layer in exporter.layers] == ["BORDE"]
    assert len(exporter.layers[0].rows) == 2


def test_rf043_layer_without_data_has_no_sheet_and_does_not_fail_the_run() -> None:
    """RF-043: an empty layer gets no sheet; with another layer with data the run succeeds."""
    interfaces = {"BORDE": [make_interface("a")], "BRAS": [make_interface("b")]}
    summary_repository = FakeDailySummaryRepository(
        [make_summary(interfaces["BORDE"][0])],
        {interfaces["BORDE"][0].id: set(RANGE.day_keys())},
    )
    service, exporter, _ = build_service(
        FakeInterfaceRepository(interfaces), summary_repository
    )
    result = service.run(RANGE)
    assert [layer.layer for layer in exporter.layers] == ["BORDE"]
    assert result.exit_code == ExitCode.SUCCESS


def test_rf044_failed_layer_fails_the_run_but_the_others_are_exported() -> None:
    """RF-044: exit code 1, yet the sheets of the successful layers are still written."""
    interfaces = {"BORDE": [make_interface("a")], "BRAS": [make_interface("b")]}
    interface_repository = FakeInterfaceRepository(
        interfaces, failing_layers=frozenset({"BORDE"})
    )
    summary_repository = FakeDailySummaryRepository(
        [make_summary(interfaces["BRAS"][0])],
        {interfaces["BRAS"][0].id: set(RANGE.day_keys())},
    )
    service, exporter, _ = build_service(interface_repository, summary_repository)
    result = service.run(RANGE)
    assert result.failed_layers == ("BORDE",)
    assert result.exit_code == ExitCode.FAILED
    assert [layer.layer for layer in exporter.layers] == ["BRAS"]
    assert len(exporter.saved_paths) == 1


def test_rf044_invalid_sheet_name_fails_that_layer_only() -> None:
    """RF-044: an invalid sheet name fails the layer, the others continue."""
    interface_repository, summary_repository = layers_with_data("BORDE", "BAD:NAME")
    exporter = FakeExporter(invalid_layer_names=frozenset({"BAD:NAME"}))
    service, exporter, _ = build_service(
        interface_repository, summary_repository, exporter
    )
    result = service.run(RANGE)
    assert result.failed_layers == ("BAD:NAME",)
    assert [layer.layer for layer in exporter.layers] == ["BORDE"]
    assert result.exit_code == ExitCode.FAILED


def test_rf044_no_layer_with_data_writes_no_file_and_fails() -> None:
    """RF-044: nothing to export: no file and exit code 1."""
    interface_repository = FakeInterfaceRepository({"BORDE": [make_interface()]})
    service, exporter, sink = build_service(
        interface_repository, FakeDailySummaryRepository([])
    )
    result = service.run(RANGE)
    assert exporter.saved_paths == []
    assert result.export_summary is None
    assert not result.export_failed
    assert result.exit_code == ExitCode.FAILED
    assert sink.of_type(FileGenerated) == []


def test_rf044_write_failure_fails_the_run_and_is_reported() -> None:
    """RF-044: a failure writing the file gives exit code 1 and an error event."""
    service, _, sink = build_service(
        *layers_with_data("BORDE"), exporter=FakeExporter(fail_on_save=True)
    )
    result = service.run(RANGE)
    assert result.export_failed
    assert result.exit_code == ExitCode.FAILED
    assert sink.of_type(ExportFailed)[0].cause == "disco lleno"
    assert sink.of_type(FileGenerated) == []


def test_rf044_no_layers_is_a_general_process_error() -> None:
    """RF-044: without any layer there is nothing to process: general error (exit 2)."""
    service, exporter, sink = build_service(
        FakeInterfaceRepository({}), FakeDailySummaryRepository([])
    )
    with pytest.raises(ProcessError, match="No hay capas"):
        service.run(RANGE)
    assert exporter.layers == []
    assert sink.events == []


def test_rf044_failure_obtaining_layers_is_a_general_process_error() -> None:
    """RF-044: a database failure while obtaining the layers is a general error (exit 2)."""
    interface_repository = FakeInterfaceRepository(
        {"BORDE": []}, fail_layer_values=True
    )
    service, exporter, _ = build_service(
        interface_repository, FakeDailySummaryRepository([])
    )
    with pytest.raises(ProcessError, match="No se pueden obtener las capas"):
        service.run(RANGE)
    assert exporter.layers == []


def test_rf036_days_without_summaries_in_any_layer_are_warned() -> None:
    """RF-036: a day missing in every successful layer is reported once; a covered day is not."""
    first, second = make_interface("a"), make_interface("b")
    interface_repository = FakeInterfaceRepository({"BORDE": [first], "BRAS": [second]})
    summary_repository = FakeDailySummaryRepository(
        [make_summary(first, days=1), make_summary(second, days=1)],
        {first.id: {"2026-03-01"}, second.id: {"2026-03-03"}},
    )
    service, _, sink = build_service(interface_repository, summary_repository)
    result = service.run(RANGE)
    assert [event.day for event in sink.of_type(MissingDay)] == ["2026-03-02"]
    assert result.missing_days == ("2026-03-02",)
    assert result.exit_code == ExitCode.SUCCESS


def test_rf036_failed_layers_do_not_count_for_the_missing_days() -> None:
    """RF-036: only layers processed successfully are evaluated."""
    failing, working = make_interface("a"), make_interface("b")
    interface_repository = FakeInterfaceRepository(
        {"BORDE": [failing], "BRAS": [working]}, failing_layers=frozenset({"BORDE"})
    )
    summary_repository = FakeDailySummaryRepository(
        [make_summary(working, days=2)], {working.id: {"2026-03-01", "2026-03-02"}}
    )
    service, _, sink = build_service(interface_repository, summary_repository)
    service.run(RANGE)
    assert [event.day for event in sink.of_type(MissingDay)] == ["2026-03-03"]


def test_rf036_no_day_is_evaluated_when_every_layer_failed() -> None:
    """RF-036: if no layer was read successfully no day is reported as missing."""
    interface_repository = FakeInterfaceRepository(
        {"BORDE": [make_interface()]}, failing_layers=frozenset({"BORDE"})
    )
    service, _, sink = build_service(
        interface_repository, FakeDailySummaryRepository([])
    )
    service.run(RANGE)
    assert sink.of_type(MissingDay) == []


def test_rf036_missing_days_do_not_fail_the_run() -> None:
    """RF-036: missing days are only warnings."""
    interface = make_interface()
    interface_repository = FakeInterfaceRepository({"BORDE": [interface]})
    summary_repository = FakeDailySummaryRepository(
        [make_summary(interface, days=1)], {interface.id: {"2026-03-01"}}
    )
    service, _, _ = build_service(interface_repository, summary_repository)
    assert service.run(RANGE).exit_code == ExitCode.SUCCESS


def test_rf042_file_name_uses_the_generation_time_and_the_export_directory() -> None:
    """RF-042: <prefix>_<generation date>.<ext> inside the export directory, not the range."""
    service, exporter, _ = build_service(*layers_with_data("BORDE"))
    service.run(RANGE)
    assert exporter.saved_paths[0].parent == EXPORT_DIRECTORY
    assert exporter.saved_paths[0].name == "ScanBackup_20261110_153000.fake"
