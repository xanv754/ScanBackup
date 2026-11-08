from datetime import UTC, datetime

import pytest

from traffic_collector.parsing import LogParser


def test_valid_line_becomes_a_utc_sample_with_float_values() -> None:
    """A line of five numbers is a sample in UTC with float values (RF-023)."""
    parsed = LogParser().parse("1762315200 100 200 300 400\n")

    sample = parsed.samples[0]
    assert sample.ts == datetime(2025, 11, 5, 4, 0, tzinfo=UTC)
    assert (sample.in_avg, sample.out_avg, sample.in_max, sample.out_max) == (100, 200, 300, 400)
    assert all(isinstance(v, float) for v in (sample.in_avg, sample.out_avg, sample.in_max))
    assert parsed.invalid_line_numbers == ()


def test_decimal_and_scientific_values_are_accepted() -> None:
    """Values may be decimals or scientific notation (RF-023)."""
    parsed = LogParser().parse("1762315200 1.5 2e3 0 4.25E+2")

    assert parsed.samples[0].out_avg == 2000.0
    assert parsed.samples[0].out_max == 425.0


@pytest.mark.parametrize(
    "line",
    [
        "1762315200 1 2 3",
        "1762315200 1 2 3 4 5",
        "abc 1 2 3 4",
        "1762315200 1 two 3 4",
        "1762315200 nan 2 3 4",
        "1762315200 inf 2 3 4",
        "99999999999999999999 1 2 3 4",
        "<html>not a log</html>",
    ],
)
def test_invalid_line_is_discarded_and_reported(line: str) -> None:
    """A line that is not five finite numbers with a valid date is discarded (RF-023)."""
    parsed = LogParser().parse(f"1762315200 1 2 3 4\n{line}\n1762315500 5 6 7 8\n")

    assert len(parsed.samples) == 2
    assert parsed.invalid_line_numbers == (2,)


def test_blank_lines_are_ignored_without_warning() -> None:
    """Blank lines are not invalid lines (RF-023)."""
    parsed = LogParser().parse("\n1762315200 1 2 3 4\n\n   \n")

    assert len(parsed.samples) == 1
    assert parsed.invalid_line_numbers == ()


def test_empty_text_has_no_samples() -> None:
    """An empty text produces no samples (RF-023)."""
    parsed = LogParser().parse("")

    assert parsed.samples == ()
    assert parsed.invalid_line_numbers == ()


def test_three_field_header_on_first_line_is_ignored_without_warning() -> None:
    """SCAN logs start with a three-field header that is not a sample."""
    parsed = LogParser().parse("1794099779 3963040349914706 8049084489756333\n1762315200 1 2 3 4\n")

    assert len(parsed.samples) == 1
    assert parsed.invalid_line_numbers == ()


def test_three_field_line_after_the_first_is_still_invalid() -> None:
    """Only the first line may be a header; later short lines are invalid."""
    parsed = LogParser().parse("1762315200 1 2 3 4\n1762315500 1 2\n")

    assert parsed.invalid_line_numbers == (2,)
