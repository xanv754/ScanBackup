import unittest
from datetime import date, time
from unittest.mock import MagicMock, patch
from bson import ObjectId
from scanbackup.application.use_case.bbip.updaters.ip_summary import (
    IPSummaryGeneratorUseCase,
)
from scanbackup.domain import IPSourceBBIPEntity, IPActiveBBIPEntity


def _source(interface: str, layer: str, source_id: ObjectId | None = None) -> IPSourceBBIPEntity:
    """Build a valid IP source entity for use-case tests."""
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
class TestIPSummaryGeneratorUseCase(unittest.TestCase):
    """Unit tests for the IPSummaryGeneratorUseCase."""

    def setUp(self) -> None:
        """Build a use case wired with mocked repositories."""
        self.source_repo = MagicMock()
        self.daily_repo = MagicMock()
        self.history_repo = MagicMock()
        self.history_repository_factory = MagicMock(return_value=self.history_repo)

    def _build_use_case(self, layers: list[str]) -> IPSummaryGeneratorUseCase:
        """Build a use case instance sharing this test's mocked collaborators."""
        return IPSummaryGeneratorUseCase(
            source_repository=self.source_repo,
            history_repository_factory=self.history_repository_factory,
            daily_repository=self.daily_repo,
            layers=layers,
            data_date="2026-01-01",
        )

    def test_execute_reads_every_configured_layer_history(self, mock_valid_layer) -> None:
        """execute() must query the history of every configured layer for the target date."""
        self.history_repo.get_by_date.return_value = []

        self._build_use_case(["IP_BRAS", "OTHER_IP"]).execute()

        self.assertEqual(self.history_repository_factory.call_count, 2)
        self.history_repository_factory.assert_any_call("IP_BRAS")
        self.history_repository_factory.assert_any_call("OTHER_IP")
        self.assertEqual(self.history_repo.get_by_date.call_count, 2)

    def test_execute_does_nothing_when_there_is_no_stored_history(
        self, mock_valid_layer
    ) -> None:
        """No stored samples for any layer must skip sources lookup and persistence entirely."""
        self.history_repo.get_by_date.return_value = []

        self._build_use_case(["IP_BRAS"]).execute()

        self.source_repo.get_all_sources.assert_not_called()
        self.daily_repo.insert.assert_not_called()

    def test_execute_summarizes_samples_from_every_layer_together(
        self, mock_valid_layer
    ) -> None:
        """Samples from every layer must be merged into a single summary pass."""
        bras_source = _source("Gi0/0/0", "IP_BRAS")
        other_source = _source("Gi0/0/1", "OTHER_IP")
        self.source_repo.get_all_sources.return_value = [bras_source, other_source]

        bras_repo = MagicMock()
        bras_repo.get_by_date.return_value = [_sample(bras_source.id)]
        other_repo = MagicMock()
        other_repo.get_by_date.return_value = [_sample(other_source.id)]
        self.history_repository_factory.side_effect = lambda layer: {
            "IP_BRAS": bras_repo,
            "OTHER_IP": other_repo,
        }[layer]

        self._build_use_case(["IP_BRAS", "OTHER_IP"]).execute()

        self.daily_repo.insert.assert_called_once()
        summarized = self.daily_repo.insert.call_args[0][0]
        self.assertEqual(len(summarized), 2)

    def test_execute_drops_samples_whose_source_is_unknown(self, mock_valid_layer) -> None:
        """A sample whose device has no matching source (even discontinued) must be dropped."""
        self.history_repo.get_by_date.return_value = [_sample(ObjectId())]
        self.source_repo.get_all_sources.return_value = []

        self._build_use_case(["IP_BRAS"]).execute()

        self.daily_repo.insert.assert_called_once_with([])


if __name__ == "__main__":
    unittest.main()
