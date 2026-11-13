import base64
import threading
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

SCAN_USERNAME = "operator"
SCAN_PASSWORD = "s3cr3t-pass"
TARGET_DAY_START = datetime(2026, 11, 5, 4, 0, tzinfo=UTC)


def build_log(count: int, step_minutes: int = 5, extra_lines: str = "") -> str:
    """A SCAN log with `count` samples of the target day (2026-11-05 in Caracas)."""
    lines = [
        f"{int((TARGET_DAY_START + timedelta(minutes=step_minutes * index)).timestamp())} "
        f"{index} {index} {index} {index}"
        for index in range(count)
    ]
    return "\n".join(lines) + "\n" + extra_lines


class ScanSimulator:
    """Local SCAN stand-in: basic auth, configurable answers per path and a request log."""

    def __init__(self) -> None:
        self.routes: dict[str, tuple[int, str]] = {}
        self.requests: list[str] = []
        self._lock = threading.Lock()
        handler = self._build_handler()
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self._server.server_address[1]}"

    def serve(self, path: str, body: str, status: int = 200) -> str:
        """Register an answer for `path` and return its full URL."""
        self.routes[path] = (status, body)
        return f"{self.base_url}{path}"

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()

    def _build_handler(self) -> type[BaseHTTPRequestHandler]:
        simulator = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                with simulator._lock:
                    simulator.requests.append(self.path)
                token = base64.b64encode(
                    f"{SCAN_USERNAME}:{SCAN_PASSWORD}".encode()
                ).decode()
                if self.headers.get("Authorization") != f"Basic {token}":
                    status, body = 401, ""
                else:
                    status, body = simulator.routes.get(self.path, (404, ""))
                payload = body.encode()
                self.send_response(status)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, format: str, *args: object) -> None:
                return

        return Handler


@pytest.fixture
def scan_simulator() -> Iterator[ScanSimulator]:
    simulator = ScanSimulator()
    simulator.start()
    yield simulator
    simulator.stop()
