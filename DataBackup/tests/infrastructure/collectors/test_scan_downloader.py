import unittest
from unittest.mock import MagicMock, patch
import requests
from scanbackup.infrastructure.collectors.scan_downloader import SCANLogDownloader

MODULE = "scanbackup.infrastructure.collectors.scan_downloader"


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


class TestSCANLogDownloader(unittest.TestCase):
    """Unit tests for the SCANLogDownloader HTTP retry/auth logic."""

    def _downloader(self) -> SCANLogDownloader:
        """Build a downloader instance with fixed credentials."""
        return SCANLogDownloader(username="user", password="pass")

    @patch(f"{MODULE}.requests.get")
    def test_download_returns_response_text(self, mock_get) -> None:
        """A successful request must return the raw response body."""
        mock_get.return_value = _response("raw-log-body")

        result = self._downloader().download("http://example.com/log")

        self.assertEqual(result, "raw-log-body")

    @patch(f"{MODULE}.requests.get")
    def test_download_retries_transient_errors_then_succeeds(self, mock_get) -> None:
        """A transient network error must be retried before giving up."""
        mock_get.side_effect = [
            requests.ConnectionError("timeout"),
            _response("raw-log-body"),
        ]

        result = self._downloader().download("http://example.com/log")

        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(result, "raw-log-body")

    @patch(f"{MODULE}.requests.get")
    def test_download_raises_after_exhausting_retries(self, mock_get) -> None:
        """Once every attempt fails, a ConnectionError must be raised."""
        mock_get.side_effect = requests.ConnectionError("timeout")

        with self.assertRaises(ConnectionError):
            self._downloader().download("http://example.com/log")
        self.assertEqual(mock_get.call_count, SCANLogDownloader._MAX_ATTEMPTS)

    @patch(f"{MODULE}.requests.get")
    def test_download_does_not_retry_on_authentication_failure(self, mock_get) -> None:
        """A 401 response must fail immediately, without consuming further retries."""
        mock_get.return_value = _response("", status_code=401)

        with self.assertRaises(requests.HTTPError):
            self._downloader().download("http://example.com/log")
        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
