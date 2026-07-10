import unittest
from unittest.mock import MagicMock
import pandas as pd
from scanbackup.application.use_case.bbip.updaters.daily_summary_traffic import (
    TrafficDailySummaryUpdaterUseCase,
    FACTOR_BBIP,
)
from scanbackup.domain import TrafficDailySummaryBBIPEntity


class TestTrafficDailySummaryUpdaterUseCase(unittest.TestCase):
    """Unit tests for the TrafficDailySummaryUpdaterUseCase."""

    def setUp(self) -> None:
        """Build a use case instance backed by a mocked repository."""
        self.repo = MagicMock()
        self.use_case = TrafficDailySummaryUpdaterUseCase(self.repo)

    def test_execute_aggregates_and_inserts_one_summary_per_interface(self) -> None:
        """execute() must average/max the raw samples and insert one entity per device."""
        data = pd.DataFrame(
            [
                {
                    "Date": "2026-01-01",
                    "Interface": "Gi0/0/0",
                    "Layer": "BORDE",
                    "Model": "Cisco",
                    "Capacity": 1000.0,
                    "In_Prom": 100.0,
                    "Out_Prom": 50.0,
                    "In_Max": 200.0,
                    "Out_Max": 100.0,
                },
                {
                    "Date": "2026-01-01",
                    "Interface": "Gi0/0/0",
                    "Layer": "BORDE",
                    "Model": "Cisco",
                    "Capacity": 1000.0,
                    "In_Prom": 200.0,
                    "Out_Prom": 150.0,
                    "In_Max": 300.0,
                    "Out_Max": 200.0,
                },
            ]
        )
        sources = pd.DataFrame(
            [
                {
                    "Interface": "Gi0/0/0",
                    "Layer": "BORDE",
                    "Model": "Cisco",
                    "Device": "68123456789abcdef0123456",
                }
            ]
        )

        self.use_case.execute(data, sources)

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

    def test_execute_drops_interfaces_missing_from_sources(self) -> None:
        """A traffic row whose interface has no matching source must be excluded."""
        data = pd.DataFrame(
            [
                {
                    "Date": "2026-01-01",
                    "Interface": "Unmatched",
                    "Layer": "BORDE",
                    "Model": "Cisco",
                    "Capacity": 1000.0,
                    "In_Prom": 100.0,
                    "Out_Prom": 50.0,
                    "In_Max": 200.0,
                    "Out_Max": 100.0,
                }
            ]
        )
        sources = pd.DataFrame(
            [{"Interface": "Other", "Layer": "BORDE", "Model": "Cisco", "Device": "abc"}]
        )

        self.use_case.execute(data, sources)

        self.repo.insert.assert_called_once_with([])


if __name__ == "__main__":
    unittest.main()
