import unittest
from datetime import date
from bson import ObjectId
from scanbackup.domain.services.bbip.traffic_report import TrafficReportService
from scanbackup.domain import TrafficSourceBBIPEntity, TrafficDailySummaryBBIPEntity


def _source(interface: str, layer: str = "BORDE", source_id: ObjectId | None = None) -> TrafficSourceBBIPEntity:
    """Build a valid active traffic source entity for service tests."""
    return TrafficSourceBBIPEntity(
        id=source_id or ObjectId(),
        link=f"http://example.com/{interface}",
        interface=interface,
        capacity=1000.0,
        model="Cisco",
        layer=layer,
    )


def _summary(device: ObjectId, day: int = 1, **overrides) -> TrafficDailySummaryBBIPEntity:
    """Build a single daily traffic summary for a device on a given day of January 2026."""
    payload = {
        "date": date(2026, 1, day),
        "in_prom": 10.0,
        "in_max": 20.0,
        "out_prom": 5.0,
        "out_max": 15.0,
        "use": 50.0,
        "device": device,
    }
    payload.update(overrides)
    return TrafficDailySummaryBBIPEntity(**payload)


class TestTrafficReportServiceBuildRows(unittest.TestCase):
    """Unit tests for TrafficReportService.build_rows."""

    def test_joins_summary_with_its_matching_source(self) -> None:
        """Each summary must be joined with the source sharing its device id."""
        source = _source("Gi0/0/0")

        rows = TrafficReportService.build_rows([source], [_summary(source.id)])

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.interface, "Gi0/0/0")
        self.assertEqual(row.model, "Cisco")
        self.assertEqual(row.capacity, 1000.0)
        self.assertEqual(row.layer, "BORDE")
        self.assertEqual(row.use, 50.0)

    def test_drops_summaries_with_no_matching_source(self) -> None:
        """A summary whose device has no matching source must be dropped."""
        rows = TrafficReportService.build_rows([], [_summary(ObjectId())])
        self.assertEqual(rows, [])


class TestTrafficReportServiceAggregateByDevice(unittest.TestCase):
    """Unit tests for TrafficReportService.aggregate_by_device."""

    def test_averages_prom_and_keeps_the_highest_max_and_use(self) -> None:
        """Prom values must be averaged; max and use values must keep the highest recorded."""
        device = ObjectId()
        summaries = [
            _summary(device, 1, in_prom=10.0, out_prom=4.0, in_max=20.0, out_max=15.0, use=40.0),
            _summary(device, 2, in_prom=20.0, out_prom=6.0, in_max=30.0, out_max=10.0, use=60.0),
        ]

        rollups = TrafficReportService.aggregate_by_device(summaries, date(2026, 1, 1))

        self.assertEqual(len(rollups), 1)
        rollup = rollups[0]
        self.assertEqual(rollup.in_prom, 15.0)
        self.assertEqual(rollup.out_prom, 5.0)
        self.assertEqual(rollup.in_max, 30.0)
        self.assertEqual(rollup.out_max, 15.0)
        self.assertEqual(rollup.use, 60.0)
        self.assertEqual(rollup.date, date(2026, 1, 1))
        self.assertEqual(rollup.device, device)

    def test_keeps_different_devices_separate(self) -> None:
        """Summaries of different devices must produce separate rollups."""
        device_a, device_b = ObjectId(), ObjectId()
        summaries = [_summary(device_a, 1), _summary(device_b, 1)]

        rollups = TrafficReportService.aggregate_by_device(summaries, date(2026, 1, 1))

        devices = {rollup.device for rollup in rollups}
        self.assertEqual(devices, {device_a, device_b})


if __name__ == "__main__":
    unittest.main()
