import unittest
from datetime import date, time
from unittest.mock import MagicMock
from bson import ObjectId
from scanbackup.application.use_case.bbip.updaters.hour_summary_ip import (
    IPHourSummaryUpdaterUseCase,
)
from scanbackup.domain import IPHourSummaryBBIPEntity, IPActiveBBIPEntity, IPSourceBBIPEntity


class TestIPHourSummaryUpdaterUseCase(unittest.TestCase):
    """Unit tests for the IPHourSummaryUpdaterUseCase."""

    def setUp(self) -> None:
        """Build a use case instance backed by a mocked repository."""
        self.repo = MagicMock()
        self.use_case = IPHourSummaryUpdaterUseCase(self.repo)

    def _sample(self, device, sample_time, in_prom, in_max) -> IPActiveBBIPEntity:
        """Build a raw active-IP sample for a given device at a given time."""
        return IPActiveBBIPEntity(
            date=date(2026, 1, 1),
            time=sample_time,
            in_prom=in_prom,
            in_max=in_max,
            device=device,
        )

    def test_execute_aggregates_samples_within_the_same_hour(self) -> None:
        """execute() must average/max samples that fall in the same round hour."""
        device = ObjectId()
        samples = [
            self._sample(device, time(13, 5, 0), 100.0, 200.0),
            self._sample(device, time(13, 55, 0), 200.0, 300.0),
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
        self.assertIsInstance(entity, IPHourSummaryBBIPEntity)

        self.assertEqual(entity.time, time(13, 0, 0))
        self.assertAlmostEqual(entity.in_prom, 150.0)
        self.assertAlmostEqual(entity.in_max, 300.0)
        self.assertEqual(entity.device, device)

    def test_execute_keeps_different_hours_separate(self) -> None:
        """Samples of the same device but different hours must produce separate summaries."""
        device = ObjectId()
        samples = [
            self._sample(device, time(13, 5, 0), 100.0, 200.0),
            self._sample(device, time(14, 5, 0), 200.0, 300.0),
        ]
        source = IPSourceBBIPEntity(
            id=device,
            link="http://example.com",
            interface="BRAS-00",
            layer="IP_BRAS",
        )

        self.use_case.execute(samples, [source])

        entities = self.repo.insert.call_args[0][0]
        self.assertEqual(len(entities), 2)
        hours = sorted(entity.time for entity in entities)
        self.assertEqual(hours, [time(13, 0, 0), time(14, 0, 0)])

    def test_execute_drops_samples_missing_from_sources(self) -> None:
        """A sample whose device has no matching source must be excluded."""
        samples = [self._sample(ObjectId(), time(13, 5, 0), 100.0, 200.0)]
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
