import unittest
from datetime import date, time
from unittest.mock import MagicMock
from bson import ObjectId
from scanbackup.application.use_case.bbip.updaters.daily_summary_ip import (
    IPDailySummaryUpdaterUseCase,
)
from scanbackup.domain import IPDailySummaryBBIPEntity, IPActiveBBIPEntity, IPSourceBBIPEntity


class TestIPDailySummaryUpdaterUseCase(unittest.TestCase):
    """Unit tests for the IPDailySummaryUpdaterUseCase."""

    def setUp(self) -> None:
        """Build a use case instance backed by a mocked repository."""
        self.repo = MagicMock()
        self.use_case = IPDailySummaryUpdaterUseCase(self.repo)

    def _sample(self, device, in_prom, in_max) -> IPActiveBBIPEntity:
        """Build a raw active-IP sample for a given device."""
        return IPActiveBBIPEntity(
            date=date(2026, 1, 1),
            time=time(10, 0, 0),
            in_prom=in_prom,
            in_max=in_max,
            device=device,
        )

    def test_execute_aggregates_and_inserts_one_summary_per_device(self) -> None:
        """execute() must average/max the raw samples and insert one entity per device."""
        device = ObjectId()
        samples = [
            self._sample(device, 100.0, 200.0),
            self._sample(device, 200.0, 300.0),
        ]
        source = IPSourceBBIPEntity(
            id=device,
            link="http://example.com",
            interface="BRAS-00",
            layer="IP_BRAS",
        )

        self.use_case.execute(samples, [source])

        self.repo.insert.assert_called_once()
        entities = self.repo.insert.call_args[0][0]
        self.assertEqual(len(entities), 1)
        entity = entities[0]
        self.assertIsInstance(entity, IPDailySummaryBBIPEntity)

        self.assertAlmostEqual(entity.in_prom, 150.0)
        self.assertAlmostEqual(entity.in_max, 300.0)
        self.assertEqual(entity.device, device)

    def test_execute_drops_samples_missing_from_sources(self) -> None:
        """A sample whose device has no matching source must be excluded."""
        samples = [self._sample(ObjectId(), 100.0, 200.0)]
        other_source = IPSourceBBIPEntity(
            id=ObjectId(),
            link="http://example.com",
            interface="Other",
            layer="IP_BRAS",
        )

        self.use_case.execute(samples, [other_source])

        self.repo.insert.assert_called_once_with([])


if __name__ == "__main__":
    unittest.main()
