from datetime import date

from reports.domain.date_range import DateRange
from reports.domain.layers import Layer
from reports.domain.period_calculator import PeriodCalculator
from reports.reporting import LayerEmpty, LayerFailed, LayerFinished, LayerIncomplete
from reports.service import LayerProcessor
from tests.fakes import (
    FakeDailySummaryRepository,
    FakeExporter,
    FakeInterfaceRepository,
    RecordingSink,
)
from tests.service.builders import make_interface, make_summary

RANGE = DateRange(start=date(2026, 3, 1), end=date(2026, 3, 3))
LAYER = Layer(name="BORDE", stored_values=("BORDE",))


def build_processor(
    interface_repository: FakeInterfaceRepository,
    summary_repository: FakeDailySummaryRepository,
    exporter: FakeExporter | None = None,
) -> tuple[LayerProcessor, RecordingSink]:
    """Build a processor with fakes and return it with its recording sink."""
    sink = RecordingSink()
    processor = LayerProcessor(
        interface_repository,
        summary_repository,
        PeriodCalculator(),
        exporter or FakeExporter(),
        sink,
    )
    return processor, sink


def test_rf043_layer_with_data_is_successful_and_gives_its_rows() -> None:
    """RF-043: a layer with interfaces and summaries is successful and has data."""
    interface = make_interface("eth-1")
    processor, sink = build_processor(
        FakeInterfaceRepository({"BORDE": [interface]}),
        FakeDailySummaryRepository([make_summary(interface)], {interface.id: {"2026-03-01"}}),
    )
    outcome = processor.process(LAYER, RANGE)
    assert not outcome.result.failed
    assert outcome.result.included_count == 1
    assert outcome.data is not None
    assert [row.name for row in outcome.data.rows] == ["ETH-1"]
    assert outcome.result.dates_with_summary == {"2026-03-01"}
    assert [type(event) for event in sink.events] == [LayerFinished]


def test_rf034_interface_without_summaries_is_not_included() -> None:
    """RF-034: only interfaces with summaries in the range appear in the report."""
    with_data, without_data = make_interface("with"), make_interface("without")
    processor, _ = build_processor(
        FakeInterfaceRepository({"BORDE": [with_data, without_data]}),
        FakeDailySummaryRepository([make_summary(with_data, days=3)]),
    )
    outcome = processor.process(LAYER, RANGE)
    assert outcome.result.included_count == 1


def test_rf043_layer_without_summaries_is_successful_but_empty() -> None:
    """RF-043: a layer without data is successful, warns and has no rows."""
    interface = make_interface()
    processor, sink = build_processor(
        FakeInterfaceRepository({"BORDE": [interface]}), FakeDailySummaryRepository([])
    )
    outcome = processor.process(LAYER, RANGE)
    assert not outcome.result.failed
    assert outcome.result.included_count == 0
    assert outcome.data is None
    assert [type(event) for event in sink.events] == [LayerEmpty, LayerFinished]


def test_rf036_incomplete_interfaces_are_counted_and_warned() -> None:
    """RF-036: interfaces with fewer summaries than days (3) are counted in a warning."""
    complete, partial_one, partial_two = (
        make_interface("a"),
        make_interface("b"),
        make_interface("c"),
    )
    processor, sink = build_processor(
        FakeInterfaceRepository({"BORDE": [complete, partial_one, partial_two]}),
        FakeDailySummaryRepository(
            [
                make_summary(complete, days=3),
                make_summary(partial_one, days=1),
                make_summary(partial_two, days=2),
            ]
        ),
    )
    outcome = processor.process(LAYER, RANGE)
    assert outcome.result.incomplete_count == 2
    assert sink.of_type(LayerIncomplete)[0].interface_count == 2
    assert not outcome.result.failed


def test_rf036_no_warning_when_every_interface_is_complete() -> None:
    """RF-036: the incomplete warning is only emitted when the count is above 0."""
    interface = make_interface()
    processor, sink = build_processor(
        FakeInterfaceRepository({"BORDE": [interface]}),
        FakeDailySummaryRepository([make_summary(interface, days=3)]),
    )
    processor.process(LAYER, RANGE)
    assert sink.of_type(LayerIncomplete) == []


def test_rf040_rows_are_sorted_by_type_then_name_then_scan_url() -> None:
    """RF-040: ascending by type, then interface; scan_url breaks ties."""
    interfaces = [
        make_interface("b", "zte"),
        make_interface("b", "huawei"),
        make_interface("a", "zte"),
        make_interface(
            "a",
            "",
        ),
    ]
    twin = make_interface("a", "zte")
    interfaces.append(twin)
    processor, _ = build_processor(
        FakeInterfaceRepository({"BORDE": interfaces}),
        FakeDailySummaryRepository([make_summary(interface) for interface in interfaces]),
    )
    outcome = processor.process(LAYER, RANGE)
    assert outcome.data is not None
    assert [(row.vendor, row.name) for row in outcome.data.rows] == [
        ("HUAWEI", "B"),
        ("UNDEFINED", "A"),
        ("ZTE", "A"),
        ("ZTE", "A"),
        ("ZTE", "B"),
    ]


def test_rf043_database_error_fails_the_layer() -> None:
    """RF-043: a database error makes the layer failed, with its cause, and no rows."""
    interface = make_interface()
    processor, sink = build_processor(
        FakeInterfaceRepository({"BORDE": [interface]}, failing_layers=frozenset({"BORDE"})),
        FakeDailySummaryRepository([]),
    )
    outcome = processor.process(LAYER, RANGE)
    assert outcome.result.failed
    assert "error de base de datos" in str(outcome.result.failure_cause)
    assert outcome.data is None
    assert [type(event) for event in sink.events] == [LayerFailed, LayerFinished]


def test_rf043_summary_read_error_fails_the_layer() -> None:
    """RF-043: an error while aggregating the summaries also fails the layer."""
    interface = make_interface()
    processor, _ = build_processor(
        FakeInterfaceRepository({"BORDE": [interface]}),
        FakeDailySummaryRepository([], failing_interfaces=frozenset({interface.id})),
    )
    assert processor.process(LAYER, RANGE).result.failed


def test_rf043_invalid_sheet_name_fails_the_layer_before_reading_data() -> None:
    """RF-043: an invalid sheet name fails the layer without querying the database."""
    interface_repository = FakeInterfaceRepository({"BAD:NAME": [make_interface()]})
    processor, sink = build_processor(
        interface_repository,
        FakeDailySummaryRepository([]),
        FakeExporter(invalid_layer_names=frozenset({"BAD:NAME"})),
    )
    outcome = processor.process(Layer("BAD:NAME", ("BAD:NAME",)), RANGE)
    assert outcome.result.failed
    assert "nombre de capa inválido" in str(outcome.result.failure_cause)
    assert interface_repository.queried_layers == []
    assert sink.of_type(LayerFailed)[0].layer == "BAD:NAME"


def test_rf034_all_stored_variants_of_the_layer_are_queried() -> None:
    """RF-034: interfaces are read with every original stored value of the canonical layer."""
    interface_repository = FakeInterfaceRepository({"BORDE": [], "borde": []})
    processor, _ = build_processor(interface_repository, FakeDailySummaryRepository([]))
    processor.process(Layer("BORDE", ("BORDE", "borde")), RANGE)
    assert interface_repository.queried_layers == [("BORDE", "borde")]
