import unittest
from datetime import datetime, date
from unittest.mock import patch
from bson import ObjectId
from scanbackup.infrastructure.collectors.mrtg_fetcher import MRTGFetcher
from scanbackup.domain.entities.bbip.traffic.source import TrafficSourceBBIPEntity
from scanbackup.domain.entities.bbip.traffic.data import TrafficBBIPEntity

MODULE = "scanbackup.infrastructure.collectors.mrtg_fetcher"


def _epoch(date_str: str) -> int:
    """Convert a YYYY-MM-DD date into a local unix timestamp, timezone-independent for tests."""
    return int(datetime.strptime(date_str, "%Y-%m-%d").replace(hour=10).timestamp())


@patch("scanbackup.domain.validator.ValidatorConfig.valid_layer_bbip")
@patch(f"{MODULE}.SCANLogDownloader")
class TestMRTGFetcher(unittest.TestCase):
    """Unit tests for the MRTGFetcher parsing logic (downloading is mocked away)."""

    def _source(self) -> TrafficSourceBBIPEntity:
        """Build a valid interface source entity for `fetch()` calls."""
        return TrafficSourceBBIPEntity(
            id=ObjectId(),
            link="http://example.com/mrtg/log",
            interface="Gi0/0/0",
            capacity=100.0,
            model="Cisco",
            layer="BORDE",
        )

    def test_fetch_returns_samples_matching_target_date(
        self, mock_downloader_cls, mock_valid_layer
    ) -> None:
        """Only samples whose date matches `target_date` must be returned as entities."""
        mock_valid_layer.return_value = True
        mock_downloader_cls.return_value.download.return_value = (
            f"{_epoch('2026-01-02')} 100 200 300 400\n"
            f"{_epoch('2026-01-01')} 999 999 999 999\n"
            "malformed line\n"
        )
        source = self._source()

        fetcher = MRTGFetcher(username="user", password="pass")
        samples = fetcher.fetch(source, target_date=date(2026, 1, 2))

        self.assertEqual(len(samples), 1)
        sample = samples[0]
        self.assertIsInstance(sample, TrafficBBIPEntity)
        self.assertEqual(sample.date, date(2026, 1, 2))
        self.assertEqual(sample.in_prom, 100.0)
        self.assertEqual(sample.out_prom, 200.0)
        self.assertEqual(sample.in_max, 300.0)
        self.assertEqual(sample.out_max, 400.0)
        self.assertEqual(sample.device, source.id)

    def test_fetch_ignores_samples_past_the_max_window(
        self, mock_downloader_cls, mock_valid_layer
    ) -> None:
        """Samples beyond the first 500 lines of the log must be discarded."""
        mock_valid_layer.return_value = True
        noise_line = f"{_epoch('2026-01-01')} 1 1 1 1"
        matching_line = f"{_epoch('2026-01-02')} 1 1 1 1"
        lines = [noise_line] * MRTGFetcher._MAX_SAMPLES + [matching_line]
        mock_downloader_cls.return_value.download.return_value = "\n".join(lines)

        fetcher = MRTGFetcher(username="user", password="pass")
        samples = fetcher.fetch(self._source(), target_date=date(2026, 1, 2))

        self.assertEqual(samples, [])

    def test_fetch_downloads_the_source_link(
        self, mock_downloader_cls, mock_valid_layer
    ) -> None:
        """fetch() must delegate the download to the shared SCANLogDownloader with the source's link."""
        mock_valid_layer.return_value = True
        mock_downloader_cls.return_value.download.return_value = ""
        source = self._source()

        MRTGFetcher(username="user", password="pass").fetch(
            source, target_date=date(2026, 1, 2)
        )

        mock_downloader_cls.return_value.download.assert_called_once_with(source.link)


if __name__ == "__main__":
    unittest.main()
