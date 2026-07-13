from datetime import datetime, date
from scanbackup.domain import TrafficSourceBBIPEntity, TrafficBBIPEntity
from scanbackup.infrastructure.collectors.scan_downloader import SCANLogDownloader


class MRTGFetcher:
    """Downloads and parses the MRTG traffic log of a single interface from SCAN."""

    _MAX_SAMPLES = 500

    def __init__(self, username: str, password: str) -> None:
        """Store the downloader used to retrieve each source's raw MRTG log."""
        self._downloader = SCANLogDownloader(username, password)

    def _parse_line(
        self, line: str
    ) -> tuple[datetime, float, float, float, float] | None:
        """Parses one MRTG log line (unix_time in_prom out_prom in_max out_max) into its typed fields."""
        fields = line.split()
        if len(fields) < 5:
            return None
        try:
            timestamp = datetime.fromtimestamp(int(fields[0]))
            in_prom, out_prom, in_max, out_max = (float(value) for value in fields[1:5])
        except (ValueError, OSError):
            return None
        return timestamp, in_prom, out_prom, in_max, out_max

    def fetch(
        self, source: TrafficSourceBBIPEntity, target_date: date
    ) -> list[TrafficBBIPEntity]:
        """Downloads the interface's MRTG log and returns its samples for `target_date`."""
        raw = self._downloader.download(source.link)
        samples: list[TrafficBBIPEntity] = []
        for line in raw.splitlines()[: self._MAX_SAMPLES]:
            parsed = self._parse_line(line)
            if not parsed:
                continue
            timestamp, in_prom, out_prom, in_max, out_max = parsed
            if timestamp.date() != target_date:
                continue
            samples.append(
                TrafficBBIPEntity(
                    date=timestamp.date(),
                    time=timestamp.time(),
                    in_prom=in_prom,
                    in_max=in_max,
                    out_prom=out_prom,
                    out_max=out_max,
                    device=source.id,
                )
            )
        return samples
