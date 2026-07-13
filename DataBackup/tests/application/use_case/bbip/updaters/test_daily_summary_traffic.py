import unittest
from datetime import date, time
from unittest.mock import MagicMock
from bson import ObjectId
from scanbackup.application.use_case.bbip.updaters.daily_summary_traffic import (
    TrafficDailySummaryUpdaterUseCase,
    FACTOR_BBIP,
)
from scanbackup.domain import TrafficDailySummaryBBIPEntity, TrafficBBIPEntity, TrafficSourceBBIPEntity


class TestTrafficDailySummaryUpdaterUseCase(unittest.TestCase):
    """Unit tests for the TrafficDailySummaryUpdaterUseCase."""

    def setUp(self) -> None:
        """Build a use case instance backed by a mocked repository."""
        self.repo = MagicMock()
        self.use_case = TrafficDailySummaryUpdaterUseCase(self.repo)

    def _sample(self, device, in_prom, out_prom, in_max, out_max) -> TrafficBBIPEntity:
        """Build a raw traffic sample for a given device."""
        return TrafficBBIPEntity(
            date=date(2026, 1, 1),
            time=time(10, 0, 0),
            in_prom=in_prom,
            out_prom=out_prom,
            in_max=in_max,
            out_max=out_max,
            device=device,
        )

    def test_execute_aggregates_and_inserts_one_summary_per_device(self) -> None:
        """execute() must average/max the raw samples and insert one entity per device."""
        device = ObjectId()
        samples = [
            self._sample(device, 100.0, 50.0, 200.0, 100.0),
            self._sample(device, 200.0, 150.0, 300.0, 200.0),
        ]
        source = TrafficSourceBBIPEntity(
            id=device,
            link="http://example.com",
            interface="Gi0/0/0",
            capacity=1000.0,
            model="Cisco",
            layer="BORDE",
        )

        self.use_case.execute(samples, [source])

        self.repo.insert.assert_called_once()
        entities = self.repo.insert.call_args[0][0]
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
        self.assertEqual(entity.device, device)

    def test_execute_drops_samples_missing_from_sources(self) -> None:
        """A sample whose device has no matching source must be excluded."""
        samples = [self._sample(ObjectId(), 100.0, 50.0, 200.0, 100.0)]
        other_source = TrafficSourceBBIPEntity(
            id=ObjectId(),
            link="http://example.com",
            interface="Other",
            capacity=1000.0,
            model="Cisco",
            layer="BORDE",
        )

        self.use_case.execute(samples, [other_source])

        self.repo.insert.assert_called_once_with([])


if __name__ == "__main__":
    unittest.main()
