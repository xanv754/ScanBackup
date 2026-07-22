import unittest
from datetime import date, time
from unittest.mock import MagicMock, patch
from bson import ObjectId
from scanbackup.application.use_case.bbip.updaters.ip_collector import (
    IPCollectorUseCase,
)
from scanbackup.domain import IPSourceBBIPEntity, IPActiveBBIPEntity


def _source(interface: str, layer: str, source_id: ObjectId | None = None) -> IPSourceBBIPEntity:
    """Build a valid active IP source entity for use-case tests."""
    return IPSourceBBIPEntity(
        id=source_id or ObjectId(),
        link=f"http://example.com/{interface}",
        interface=interface,
        layer=layer,
    )


def _sample(device: ObjectId) -> IPActiveBBIPEntity:
    """Build a single raw active-IP sample for a device."""
    return IPActiveBBIPEntity(
        date=date(2026, 1, 1),
        time=time(10, 0, 0),
        in_prom=120.0,
        in_max=150.0,
        device=device,
    )


@patch("scanbackup.domain.validator.ValidatorConfig.valid_layer_ip", return_value=True)
class TestIPCollectorUseCase(unittest.TestCase):
    """Unit tests for the IPCollectorUseCase."""

    def setUp(self) -> None:
        """Build a use case wired with mocked repositories and fetcher."""
        self.source_repo = MagicMock()
        self.history_repo = MagicMock()
        self.history_repository_factory = MagicMock(return_value=self.history_repo)
        self.fetcher = MagicMock()

    def _build_use_case(self, max_workers: int = 1) -> IPCollectorUseCase:
        """Build a use case instance sharing this test's mocked collaborators."""
        return IPCollectorUseCase(
            source_repository=self.source_repo,
            history_repository_factory=self.history_repository_factory,
            fetcher=self.fetcher,
            data_date="2026-01-01",
            max_workers=max_workers,
        )

    def test_execute_does_nothing_when_there_are_no_active_sources(
        self, mock_valid_layer
    ) -> None:
        """No active sources must skip fetching and persisting entirely."""
        self.source_repo.get_all_active_sources.return_value = []

        self._build_use_case().execute()

        self.fetcher.fetch.assert_not_called()
        self.history_repository_factory.assert_not_called()

    def test_execute_fetches_every_active_source_regardless_of_layer(
        self, mock_valid_layer
    ) -> None:
        """Sources of every layer must be queried once, without a per-layer filter."""
        bras_ip = _source("Gi0/0/0", "IP_BRAS")
        other = _source("Gi0/0/1", "OTHER_IP")
        self.source_repo.get_all_active_sources.return_value = [bras_ip, other]
        self.fetcher.fetch.side_effect = lambda source, target_date: [_sample(source.id)]

        self._build_use_case().execute()

        self.assertEqual(self.fetcher.fetch.call_count, 2)
        self.source_repo.get_sources_by_layer.assert_not_called()

    def test_execute_inserts_samples_into_the_matching_layer_history(
        self, mock_valid_layer
    ) -> None:
        """Each layer's samples must be inserted through its own history repository."""
        bras_ip = _source("Gi0/0/0", "IP_BRAS")
        other = _source("Gi0/0/1", "OTHER_IP")
        self.source_repo.get_all_active_sources.return_value = [bras_ip, other]
        self.fetcher.fetch.side_effect = lambda source, target_date: [_sample(source.id)]

        self._build_use_case().execute()

        self.assertEqual(self.history_repository_factory.call_count, 2)
        self.history_repository_factory.assert_any_call("IP_BRAS")
        self.history_repository_factory.assert_any_call("OTHER_IP")
        self.assertEqual(self.history_repo.insert.call_count, 2)

    def test_a_single_source_failure_does_not_abort_the_others(
        self, mock_valid_layer
    ) -> None:
        """A source whose fetch raises must be skipped without stopping the batch."""
        ok_source = _source("Gi0/0/0", "IP_BRAS")
        bad_source = _source("Gi0/0/1", "IP_BRAS")
        self.source_repo.get_all_active_sources.return_value = [ok_source, bad_source]

        def fetch(source, target_date):
            if source is bad_source:
                raise ConnectionError("network down")
            return [_sample(source.id)]

        self.fetcher.fetch.side_effect = fetch

        self._build_use_case().execute()

        self.history_repo.insert.assert_called_once()
        inserted = self.history_repo.insert.call_args[0][0]
        self.assertEqual(len(inserted), 1)

    def test_execute_skips_persistence_when_every_fetch_yields_no_samples(
        self, mock_valid_layer
    ) -> None:
        """If every source returns no samples for the date, nothing must be persisted."""
        source = _source("Gi0/0/0", "IP_BRAS")
        self.source_repo.get_all_active_sources.return_value = [source]
        self.fetcher.fetch.return_value = []

        self._build_use_case().execute()

        self.history_repository_factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
