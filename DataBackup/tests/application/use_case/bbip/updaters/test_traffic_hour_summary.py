import unittest
from datetime import date, time
from unittest.mock import MagicMock
from bson import ObjectId
from scanbackup.application.use_case.bbip.updaters.traffic_hour_summary import (
    TrafficHourSummaryGeneratorUseCase,
)
from scanbackup.domain import TrafficSourceBBIPEntity, TrafficBBIPEntity


def _source(interface: str, layer: str, source_id: ObjectId | None = None) -> TrafficSourceBBIPEntity:
    """Build a valid traffic source entity for use-case tests."""
    return TrafficSourceBBIPEntity(
        id=source_id or ObjectId(),
        link=f"http://example.com/{interface}",
        interface=interface,
        capacity=1000.0,
        model="Cisco",
        layer=layer,
    )


def _sample(device: ObjectId) -> TrafficBBIPEntity:
    """Build a single raw traffic sample for a device."""
    return TrafficBBIPEntity(
        date=date(2026, 1, 1),
        time=time(10, 0, 0),
        in_prom=100.0,
        out_prom=50.0,
        in_max=200.0,
        out_max=100.0,
        device=device,
    )


class TestTrafficHourSummaryGeneratorUseCase(unittest.TestCase):
    """Unit tests for the TrafficHourSummaryGeneratorUseCase."""

    def setUp(self) -> None:
        """Build a use case wired with mocked repositories."""
        self.source_repo = MagicMock()
        self.hour_repo = MagicMock()
        self.history_repo = MagicMock()
        self.history_repository_factory = MagicMock(return_value=self.history_repo)

    def _build_use_case(self, layers: list[str]) -> TrafficHourSummaryGeneratorUseCase:
        """Build a use case instance sharing this test's mocked collaborators."""
        return TrafficHourSummaryGeneratorUseCase(
            source_repository=self.source_repo,
            history_repository_factory=self.history_repository_factory,
            hour_repository=self.hour_repo,
            layers=layers,
            data_date="2026-01-01",
        )

    def test_execute_reads_every_configured_layer_history(self) -> None:
        """execute() must query the history of every configured layer for the target date."""
        self.history_repo.get_by_date.return_value = []

        self._build_use_case(["BORDE", "DINT"]).execute()

        self.assertEqual(self.history_repository_factory.call_count, 2)
        self.history_repository_factory.assert_any_call("BORDE")
        self.history_repository_factory.assert_any_call("DINT")
        self.assertEqual(self.history_repo.get_by_date.call_count, 2)

    def test_execute_does_nothing_when_there_is_no_stored_history(self) -> None:
        """No stored samples for any layer must skip sources lookup and persistence entirely."""
        self.history_repo.get_by_date.return_value = []

        self._build_use_case(["BORDE"]).execute()

        self.source_repo.get_all_sources.assert_not_called()
        self.hour_repo.insert.assert_not_called()

    def test_execute_summarizes_samples_from_every_layer_together(self) -> None:
        """Samples from every layer must be merged into a single summary pass."""
        borde_source = _source("Gi0/0/0", "BORDE")
        dint_source = _source("Gi0/0/1", "DINT")
        self.source_repo.get_all_sources.return_value = [borde_source, dint_source]

        borde_repo = MagicMock()
        borde_repo.get_by_date.return_value = [_sample(borde_source.id)]
        dint_repo = MagicMock()
        dint_repo.get_by_date.return_value = [_sample(dint_source.id)]
        self.history_repository_factory.side_effect = lambda layer: {
            "BORDE": borde_repo,
            "DINT": dint_repo,
        }[layer]

        self._build_use_case(["BORDE", "DINT"]).execute()

        self.hour_repo.insert.assert_called_once()
        summarized = self.hour_repo.insert.call_args[0][0]
        self.assertEqual(len(summarized), 2)

    def test_execute_drops_samples_whose_source_is_unknown(self) -> None:
        """A sample whose device has no matching source (even discontinued) must be dropped."""
        self.history_repo.get_by_date.return_value = [_sample(ObjectId())]
        self.source_repo.get_all_sources.return_value = []

        self._build_use_case(["BORDE"]).execute()

        self.hour_repo.insert.assert_called_once_with([])


if __name__ == "__main__":
    unittest.main()
