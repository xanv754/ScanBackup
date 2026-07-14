import unittest
from datetime import date, time
from bson import ObjectId
from scanbackup.domain.services.bbip.traffic_summary import (
    TrafficSummaryService,
    FACTOR_BBIP,
)
from scanbackup.domain import (
    TrafficBBIPEntity,
    TrafficSourceBBIPEntity,
    TrafficDailySummaryBBIPEntity,
    TrafficHourSummaryBBIPEntity,
)


def _source(interface: str = "Gi0/0/0", capacity: float = 1000.0, source_id: ObjectId | None = None) -> TrafficSourceBBIPEntity:
    """Build a valid active traffic source entity for service tests."""
    return TrafficSourceBBIPEntity(
        id=source_id or ObjectId(),
        link=f"http://example.com/{interface}",
        interface=interface,
        capacity=capacity,
        model="Cisco",
        layer="BORDE",
    )


def _sample(
    device: ObjectId, in_prom: float, out_prom: float, in_max: float, out_max: float, sample_time: time = time(10, 0, 0)
) -> TrafficBBIPEntity:
    """Build a raw traffic sample for a given device."""
    return TrafficBBIPEntity(
        date=date(2026, 1, 1),
        time=sample_time,
        in_prom=in_prom,
        out_prom=out_prom,
        in_max=in_max,
        out_max=out_max,
        device=device,
    )


class TestTrafficSummaryServiceSummarizeByDate(unittest.TestCase):
    """Unit tests for TrafficSummaryService.summarize_by_date."""

    def test_averages_and_maxes_samples_of_the_same_device(self) -> None:
        """Samples of the same device-day must produce one averaged/maxed summary, converted by FACTOR_BBIP."""
        source = _source(capacity=1000.0)
        samples = [
            _sample(source.id, 100.0, 50.0, 200.0, 100.0),
            _sample(source.id, 200.0, 150.0, 300.0, 200.0),
        ]

        entities = TrafficSummaryService.summarize_by_date(samples, [source])

        self.assertEqual(len(entities), 1)
        entity = entities[0]
        self.assertIsInstance(entity, TrafficDailySummaryBBIPEntity)

        expected_in_max = 300.0 * FACTOR_BBIP
        expected_out_max = 200.0 * FACTOR_BBIP
        expected_use = max(expected_in_max, expected_out_max) / 1000.0 * 100
        self.assertAlmostEqual(entity.in_prom, 150.0 * FACTOR_BBIP)
        self.assertAlmostEqual(entity.out_prom, 100.0 * FACTOR_BBIP)
        self.assertAlmostEqual(entity.in_max, expected_in_max)
        self.assertAlmostEqual(entity.out_max, expected_out_max)
        self.assertAlmostEqual(entity.use, expected_use)
        self.assertEqual(entity.device, source.id)

    def test_drops_samples_missing_from_sources(self) -> None:
        """A sample whose device has no matching source must be excluded."""
        samples = [_sample(ObjectId(), 100.0, 50.0, 200.0, 100.0)]
        other_source = _source(interface="Other")

        entities = TrafficSummaryService.summarize_by_date(samples, [other_source])

        self.assertEqual(entities, [])


class TestTrafficSummaryServiceSummarizeByHour(unittest.TestCase):
    """Unit tests for TrafficSummaryService.summarize_by_hour."""

    def test_aggregates_samples_within_the_same_hour(self) -> None:
        """Samples within the same round hour must be aggregated into one summary."""
        source = _source(capacity=1000.0)
        samples = [
            _sample(source.id, 100.0, 50.0, 200.0, 100.0, time(13, 5, 0)),
            _sample(source.id, 200.0, 150.0, 300.0, 200.0, time(13, 55, 0)),
        ]

        entities = TrafficSummaryService.summarize_by_hour(samples, [source])

        self.assertEqual(len(entities), 1)
        entity = entities[0]
        self.assertIsInstance(entity, TrafficHourSummaryBBIPEntity)
        self.assertEqual(entity.time, time(13, 0, 0))

        expected_in_max = 300.0 * FACTOR_BBIP
        expected_out_max = 200.0 * FACTOR_BBIP
        expected_use = max(expected_in_max, expected_out_max) / 1000.0 * 100
        self.assertAlmostEqual(entity.in_prom, 150.0 * FACTOR_BBIP)
        self.assertAlmostEqual(entity.out_prom, 100.0 * FACTOR_BBIP)
        self.assertAlmostEqual(entity.in_max, expected_in_max)
        self.assertAlmostEqual(entity.out_max, expected_out_max)
        self.assertAlmostEqual(entity.use, expected_use)
        self.assertEqual(entity.device, source.id)

    def test_keeps_different_hours_separate(self) -> None:
        """Samples of the same device but different hours must produce separate summaries."""
        source = _source(capacity=1000.0)
        samples = [
            _sample(source.id, 100.0, 50.0, 200.0, 100.0, time(13, 5, 0)),
            _sample(source.id, 200.0, 150.0, 300.0, 200.0, time(14, 5, 0)),
        ]

        entities = TrafficSummaryService.summarize_by_hour(samples, [source])

        self.assertEqual(len(entities), 2)
        hours = sorted(entity.time for entity in entities)
        self.assertEqual(hours, [time(13, 0, 0), time(14, 0, 0)])

    def test_drops_samples_missing_from_sources(self) -> None:
        """A sample whose device has no matching source must be excluded."""
        samples = [_sample(ObjectId(), 100.0, 50.0, 200.0, 100.0, time(13, 5, 0))]
        other_source = _source(interface="Other")

        entities = TrafficSummaryService.summarize_by_hour(samples, [other_source])

        self.assertEqual(entities, [])


if __name__ == "__main__":
    unittest.main()
