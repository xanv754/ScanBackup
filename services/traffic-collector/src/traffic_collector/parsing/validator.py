from traffic_collector.constants.constants import EXPECTED_SAMPLES_PER_DAY
from traffic_collector.constants.enums import SampleCountVerdict


class SampleValidator:
    """Applies the rules of the 288 daily samples. Pure."""

    def evaluate(self, sample_count: int) -> SampleCountVerdict:
        """Classify the amount of valid samples of the day [RF-024].

        EMPTY (0) makes the interface fail; PARTIAL (1-287) and EXCESS (>288) are stored with a
        warning; COMPLETE is exactly 288.
        """
        if sample_count == 0:
            return SampleCountVerdict.EMPTY
        if sample_count < EXPECTED_SAMPLES_PER_DAY:
            return SampleCountVerdict.PARTIAL
        if sample_count > EXPECTED_SAMPLES_PER_DAY:
            return SampleCountVerdict.EXCESS
        return SampleCountVerdict.COMPLETE
