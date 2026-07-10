from datetime import datetime
import requests
import urllib3
from scanbackup.domain import TrafficSourceBBIPEntity
from scanbackup.shared import SCANHeader

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MRTGFetcher:
    """Downloads and parses the MRTG traffic log of a single interface from SCAN."""

    _MAX_SAMPLES = 500
    _TIMEOUT_SECONDS = 180
    _MAX_ATTEMPTS = 2
    _TIME_FORMAT = "%H:%M:%S"

    def __init__(self, username: str, password: str, delimiter: str, date_format: str) -> None:
        """Store the SCAN credentials and formatting rules used to build output rows."""
        self._auth = (username, password)
        self._delimiter = delimiter
        self._date_format = date_format

    def _download(self, url: str) -> str:
        """Downloads the raw MRTG log for `url`, retrying transient failures but not authentication errors."""
        last_error: Exception | None = None
        for _ in range(self._MAX_ATTEMPTS):
            try:
                response = requests.get(
                    url, auth=self._auth, timeout=self._TIMEOUT_SECONDS, verify=False
                )
                response.raise_for_status()
                return response.text
            except requests.HTTPError as error:
                if error.response is not None and error.response.status_code == 401:
                    raise
                last_error = error
            except requests.RequestException as error:
                last_error = error
        raise ConnectionError(f"Fallo al descargar {url}") from last_error

    def _parse_line(self, line: str) -> tuple[datetime, str, str, str, str] | None:
        """Parses one MRTG log line (unix_time in_prom out_prom in_max out_max) into its fields."""
        fields = line.split()
        if len(fields) < 5:
            return None
        try:
            timestamp = datetime.fromtimestamp(int(fields[0]))
        except (ValueError, OSError):
            return None
        return timestamp, fields[1], fields[2], fields[3], fields[4]

    def _build_row(
        self,
        source: TrafficSourceBBIPEntity,
        timestamp: datetime,
        file_date: str,
        in_prom: str,
        out_prom: str,
        in_max: str,
        out_max: str,
    ) -> str:
        """Formats a single output row matching the SCANHeader column order."""
        values = {
            SCANHeader.INTERFACE: source.interface,
            SCANHeader.CAPACITY: str(source.capacity),
            SCANHeader.MODEL: source.model,
            SCANHeader.DATE: file_date,
            SCANHeader.TIME: timestamp.strftime(self._TIME_FORMAT),
            SCANHeader.IN_PROM: in_prom,
            SCANHeader.OUT_PROM: out_prom,
            SCANHeader.IN_MAX: in_max,
            SCANHeader.OUT_MAX: out_max,
            SCANHeader.LAYER: source.layer,
        }
        return self._delimiter.join(values[header] for header in SCANHeader)

    def fetch(self, source: TrafficSourceBBIPEntity, target_date: str) -> list[str]:
        """Downloads the interface's MRTG log and returns its formatted rows for `target_date`."""
        raw = self._download(source.link)
        rows: list[str] = []
        for line in raw.splitlines()[: self._MAX_SAMPLES]:
            parsed = self._parse_line(line)
            if not parsed:
                continue
            timestamp, in_prom, out_prom, in_max, out_max = parsed
            file_date = timestamp.strftime(self._date_format)
            if file_date != target_date:
                continue
            rows.append(
                self._build_row(
                    source, timestamp, file_date, in_prom, out_prom, in_max, out_max
                )
            )
        return rows
