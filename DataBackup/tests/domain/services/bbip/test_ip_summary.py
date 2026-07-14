import unittest
from datetime import date, time
from bson import ObjectId
from scanbackup.domain.services.bbip.ip_summary import IPSummaryService
from scanbackup.domain import (
    IPActiveBBIPEntity,
    IPSourceBBIPEntity,
    IPDailySummaryBBIPEntity,
    IPHourSummaryBBIPEntity,
)


def _source(interface: str = "BRAS-00", source_id: ObjectId | None = None) -> IPSourceBBIPEntity:
    """Build a valid active IP source entity for service tests."""
    return IPSourceBBIPEntity(
        id=source_id or ObjectId(),
        link="http://example.com",
        interface=interface,
        layer="IP_BRAS",
    )


def _sample(device: ObjectId, in_prom: float, in_max: float, sample_time: time = time(10, 0, 0)) -> IPActiveBBIPEntity:
    """Build a raw active-IP sample for a given device."""
    return IPActiveBBIPEntity(
        date=date(2026, 1, 1), time=sample_time, in_prom=in_prom, in_max=in_max, device=device
    )


class TestIPSummaryServiceSummarizeByDate(unittest.TestCase):
    """Unit tests for IPSummaryService.summarize_by_date."""

    def test_averages_and_maxes_samples_of_the_same_device(self) -> None:
        """Samples of the same device-day must produce one averaged/maxed summary."""
        source = _source()
        samples = [_sample(source.id, 100.0, 200.0), _sample(source.id, 200.0, 300.0)]

        entities = IPSummaryService.summarize_by_date(samples, [source])

        self.assertEqual(len(entities), 1)
        entity = entities[0]
        self.assertIsInstance(entity, IPDailySummaryBBIPEntity)
        self.assertAlmostEqual(entity.in_prom, 150.0)
        self.assertAlmostEqual(entity.in_max, 300.0)
        self.assertEqual(entity.device, source.id)

    def test_drops_samples_missing_from_sources(self) -> None:
        """A sample whose device has no matching source must be excluded."""
        samples = [_sample(ObjectId(), 100.0, 200.0)]
        other_source = _source(interface="Other")

        entities = IPSummaryService.summarize_by_date(samples, [other_source])

        self.assertEqual(entities, [])


class TestIPSummaryServiceSummarizeByHour(unittest.TestCase):
    """Unit tests for IPSummaryService.summarize_by_hour."""

    def test_aggregates_samples_within_the_same_hour(self) -> None:
        """Samples within the same round hour must be aggregated into one summary."""
        source = _source()
        samples = [
            _sample(source.id, 100.0, 200.0, time(13, 5, 0)),
            _sample(source.id, 200.0, 300.0, time(13, 55, 0)),
        ]

        entities = IPSummaryService.summarize_by_hour(samples, [source])

        self.assertEqual(len(entities), 1)
        entity = entities[0]
        self.assertIsInstance(entity, IPHourSummaryBBIPEntity)
        self.assertEqual(entity.time, time(13, 0, 0))
        self.assertAlmostEqual(entity.in_prom, 150.0)
        self.assertAlmostEqual(entity.in_max, 300.0)
        self.assertEqual(entity.device, source.id)

    def test_keeps_different_hours_separate(self) -> None:
        """Samples of the same device but different hours must produce separate summaries."""
        source = _source()
        samples = [
            _sample(source.id, 100.0, 200.0, time(13, 5, 0)),
            _sample(source.id, 200.0, 300.0, time(14, 5, 0)),
        ]

        entities = IPSummaryService.summarize_by_hour(samples, [source])

        self.assertEqual(len(entities), 2)
        hours = sorted(entity.time for entity in entities)
        self.assertEqual(hours, [time(13, 0, 0), time(14, 0, 0)])

    def test_drops_samples_missing_from_sources(self) -> None:
        """A sample whose device has no matching source must be excluded."""
        samples = [_sample(ObjectId(), 100.0, 200.0, time(13, 5, 0))]
        other_source = _source(interface="Other")

        entities = IPSummaryService.summarize_by_hour(samples, [other_source])

        self.assertEqual(entities, [])


if __name__ == "__main__":
    unittest.main()
