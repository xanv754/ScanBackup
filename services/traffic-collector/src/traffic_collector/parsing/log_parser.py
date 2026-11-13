import math
from dataclasses import dataclass
from datetime import UTC, datetime

from traffic_collector.constants.constants import (
    LOG_FIELDS_PER_LINE,
    LOG_HEADER_FIELDS_PER_LINE,
)
from traffic_collector.domain import Sample


@dataclass(frozen=True, slots=True)
class ParsedLog:
    """Valid samples of a SCAN log and the numbers of the lines that were discarded."""

    samples: tuple[Sample, ...]
    invalid_line_numbers: tuple[int, ...]


class LogParser:
    """Converts the text of a SCAN traffic log into samples. Pure: no network, no database."""

    def parse(self, text: str) -> ParsedLog:
        """Parse every line `<unix date> <in avg> <out avg> <in max> <out max>` [RF-023].

        Blank lines are ignored, and so is the three-field header that SCAN writes as the first
        line of every log. A line without exactly five finite numeric fields, or with a
        date that is not a valid UNIX time, is discarded and its number is reported.
        Sample dates are returned in UTC and the values as `float`.
        """
        samples: list[Sample] = []
        invalid_line_numbers: list[int] = []
        is_first_content_line = True
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            if is_first_content_line:
                is_first_content_line = False
                if len(line.split()) == LOG_HEADER_FIELDS_PER_LINE:
                    continue
            sample = self._parse_line(line)
            if sample is None:
                invalid_line_numbers.append(line_number)
            else:
                samples.append(sample)
        return ParsedLog(samples=tuple(samples), invalid_line_numbers=tuple(invalid_line_numbers))

    @staticmethod
    def _parse_line(line: str) -> Sample | None:
        """Return the sample of one line, or None when the line is invalid."""
        fields = line.split()
        if len(fields) != LOG_FIELDS_PER_LINE:
            return None
        try:
            unix_date, in_avg, out_avg, in_max, out_max = (float(field) for field in fields)
        except ValueError:
            return None
        if not all(math.isfinite(value) for value in (unix_date, in_avg, out_avg, in_max, out_max)):
            return None
        try:
            moment = datetime.fromtimestamp(unix_date, tz=UTC)
        except (OverflowError, OSError, ValueError):
            return None
        return Sample(ts=moment, in_avg=in_avg, out_avg=out_avg, in_max=in_max, out_max=out_max)
