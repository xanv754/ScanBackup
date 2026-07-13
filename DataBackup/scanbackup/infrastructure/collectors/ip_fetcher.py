from datetime import datetime, date
from scanbackup.domain import IPSourceBBIPEntity, IPActiveBBIPEntity
from scanbackup.infrastructure.collectors.scan_downloader import SCANLogDownloader


class IPActiveFetcher:
    """Downloads and parses the active-IP-count log of a single interface from SCAN."""

    _MAX_SAMPLES = 500

    def __init__(self, username: str, password: str) -> None:
        """Store the downloader used to retrieve each source's raw active-IP log."""
        self._downloader = SCANLogDownloader(username, password)

    def _parse_line(self, line: str) -> tuple[datetime, float, float] | None:
        """Parses one SCAN log line (unix_time in_prom in_max) into its typed fields."""
        fields = line.split()
        if len(fields) < 3:
            return None
        try:
            timestamp = datetime.fromtimestamp(int(fields[0]))
            in_prom, in_max = (float(value) for value in fields[1:3])
        except (ValueError, OSError):
            return None
        return timestamp, in_prom, in_max

    def fetch(
        self, source: IPSourceBBIPEntity, target_date: date
    ) -> list[IPActiveBBIPEntity]:
        """Downloads the interface's active-IP log and returns its samples for `target_date`."""
        raw = self._downloader.download(source.link)
        samples: list[IPActiveBBIPEntity] = []
        for line in raw.splitlines()[: self._MAX_SAMPLES]:
            parsed = self._parse_line(line)
            if not parsed:
                continue
            timestamp, in_prom, in_max = parsed
            if timestamp.date() != target_date:
                continue
            samples.append(
                IPActiveBBIPEntity(
                    date=timestamp.date(),
                    time=timestamp.time(),
                    in_prom=in_prom,
                    in_max=in_max,
                    device=source.id,
                )
            )
        return samples
