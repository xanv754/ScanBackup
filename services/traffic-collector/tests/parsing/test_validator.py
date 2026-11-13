import pytest

from traffic_collector.constants.enums import SampleCountVerdict
from traffic_collector.parsing import SampleValidator


@pytest.mark.parametrize(
    ("sample_count", "expected"),
    [
        (0, SampleCountVerdict.EMPTY),
        (1, SampleCountVerdict.PARTIAL),
        (287, SampleCountVerdict.PARTIAL),
        (288, SampleCountVerdict.COMPLETE),
        (289, SampleCountVerdict.EXCESS),
    ],
)
def test_sample_count_verdict(sample_count: int, expected: SampleCountVerdict) -> None:
    """0 fails; 1-287 and 289+ warn; 288 is complete (RF-024)."""
    assert SampleValidator().evaluate(sample_count) == expected
