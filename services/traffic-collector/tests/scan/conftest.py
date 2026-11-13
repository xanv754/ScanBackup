import base64
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

USERNAME = "operator"
PASSWORD = "secret"
LOG_BODY = "1762315200 1 2 3 4\n"
HANG_SECONDS = 1.0


class ScanSimulatorHandler(BaseHTTPRequestHandler):
    """Minimal SCAN stand-in: basic auth plus one path per failure mode."""

    def do_GET(self) -> None:
        expected = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
        if self.headers.get("Authorization") != f"Basic {expected}":
            self._answer(401, "")
        elif self.path == "/ok.log":
            self._answer(200, LOG_BODY)
        elif self.path == "/empty.log":
            self._answer(200, "  \n")
        elif self.path == "/error.log":
            self._answer(500, "boom")
        elif self.path == "/hang.log":
            time.sleep(HANG_SECONDS)
            self._answer(200, LOG_BODY)
        else:
            self._answer(404, "")

    def _answer(self, status: int, body: str) -> None:
        payload = body.encode()
        try:
            self.send_response(status)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            return

    def log_message(self, format: str, *args: object) -> None:
        return


@pytest.fixture(scope="module")
def scan_simulator_url() -> Iterator[str]:
    """Base URL of a local SCAN simulator running in a background thread."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), ScanSimulatorHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()
