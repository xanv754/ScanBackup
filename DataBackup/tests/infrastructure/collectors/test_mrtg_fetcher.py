import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
import requests
from scanbackup.infrastructure.collectors.mrtg_fetcher import MRTGFetcher
from scanbackup.domain.entities.bbip.traffic.source import TrafficSourceBBIPEntity

MODULE = "scanbackup.infrastructure.collectors.mrtg_fetcher"


def _epoch(date_str: str) -> int:
    """Convert a YYYY-MM-DD date into a local unix timestamp, timezone-independent for tests."""
    return int(datetime.strptime(date_str, "%Y-%m-%d").replace(hour=10).timestamp())


def _response(text: str, status_code: int = 200) -> MagicMock:
    """Build a fake `requests.Response` exposing `.text` and `.raise_for_status()`."""
    response = MagicMock()
    response.text = text
    response.status_code = status_code
    if status_code >= 400:
        error = requests.HTTPError(response=response)
        response.raise_for_status.side_effect = error
    else:
        response.raise_for_status.side_effect = None
    return response


@patch("scanbackup.domain.services.validator.ValidatorConfig.valid_layer_bbip")
class TestMRTGFetcher(unittest.TestCase):
    """Unit tests for the MRTGFetcher HTTP downloader/parser."""

    def _source(self) -> TrafficSourceBBIPEntity:
        """Build a valid interface source entity for `fetch()` calls."""
        return TrafficSourceBBIPEntity(
            link="http://example.com/mrtg/log",
            interface="Gi0/0/0",
            capacity=100.0,
            model="Cisco",
            layer="BORDE",
        )

    def _fetcher(self) -> MRTGFetcher:
        """Build a fetcher instance with fixed credentials and formatting rules."""
        return MRTGFetcher(
            username="user", password="pass", delimiter=";", date_format="%Y-%m-%d"
        )

    @patch(f"{MODULE}.requests.get")
    def test_fetch_returns_rows_matching_target_date(
        self, mock_get, mock_valid_layer
    ) -> None:
        """Only samples whose date matches `target_date` must be returned, correctly formatted."""
        mock_valid_layer.return_value = True
        mock_get.return_value = _response(
            f"{_epoch('2026-01-02')} 100 200 300 400\n"
            f"{_epoch('2026-01-01')} 999 999 999 999\n"
            "malformed line\n"
        )

        fetcher = self._fetcher()
        rows = fetcher.fetch(self._source(), target_date="2026-01-02")

        self.assertEqual(len(rows), 1)
        fields = rows[0].split(";")
        self.assertEqual(fields[0], "Gi0/0/0")
        self.assertEqual(fields[1], "100.0")
        self.assertEqual(fields[2], "Cisco")
        self.assertEqual(fields[3], "2026-01-02")
        self.assertEqual(fields[5], "100")
        self.assertEqual(fields[6], "200")
        self.assertEqual(fields[7], "300")
        self.assertEqual(fields[8], "400")
        self.assertEqual(fields[9], "BORDE")

    @patch(f"{MODULE}.requests.get")
    def test_fetch_ignores_samples_past_the_max_window(
        self, mock_get, mock_valid_layer
    ) -> None:
        """Samples beyond the first 500 lines of the log must be discarded."""
        mock_valid_layer.return_value = True
        noise_line = f"{_epoch('2026-01-01')} 1 1 1 1"
        matching_line = f"{_epoch('2026-01-02')} 1 1 1 1"
        lines = [noise_line] * MRTGFetcher._MAX_SAMPLES + [matching_line]
        mock_get.return_value = _response("\n".join(lines))

        fetcher = self._fetcher()
        rows = fetcher.fetch(self._source(), target_date="2026-01-02")

        self.assertEqual(rows, [])

    @patch(f"{MODULE}.requests.get")
    def test_download_retries_transient_errors_then_succeeds(
        self, mock_get, mock_valid_layer
    ) -> None:
        """A transient network error must be retried before giving up."""
        mock_valid_layer.return_value = True
        mock_get.side_effect = [
            requests.ConnectionError("timeout"),
            _response(f"{_epoch('2026-01-02')} 1 2 3 4"),
        ]

        fetcher = self._fetcher()
        rows = fetcher.fetch(self._source(), target_date="2026-01-02")

        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(len(rows), 1)

    @patch(f"{MODULE}.requests.get")
    def test_download_raises_after_exhausting_retries(
        self, mock_get, mock_valid_layer
    ) -> None:
        """Once every attempt fails, a ConnectionError must be raised."""
        mock_valid_layer.return_value = True
        mock_get.side_effect = requests.ConnectionError("timeout")

        fetcher = self._fetcher()
        with self.assertRaises(ConnectionError):
            fetcher.fetch(self._source(), target_date="2026-01-02")
        self.assertEqual(mock_get.call_count, MRTGFetcher._MAX_ATTEMPTS)

    @patch(f"{MODULE}.requests.get")
    def test_download_does_not_retry_on_authentication_failure(
        self, mock_get, mock_valid_layer
    ) -> None:
        """A 401 response must fail immediately, without consuming further retries."""
        mock_valid_layer.return_value = True
        mock_get.return_value = _response("", status_code=401)

        fetcher = self._fetcher()
        with self.assertRaises(requests.HTTPError):
            fetcher.fetch(self._source(), target_date="2026-01-02")
        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
