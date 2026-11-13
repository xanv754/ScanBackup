import io
import os
import uuid
from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database

from tests.integration.conftest import SCAN_PASSWORD, SCAN_USERNAME, ScanSimulator, build_log
from traffic_collector.cli import execute
from traffic_collector.constants.enums import ExitCode

pytestmark = pytest.mark.integration

TODAY = date(2026, 11, 6)
TARGET_DATE = "2026-11-05"


class Harness:
    """Runs the real `execute` against a throwaway database and the SCAN simulator."""

    def __init__(self, database: Database, simulator: ScanSimulator, tmp_path: Path) -> None:
        self.database = database
        self.simulator = simulator
        self.log_path = tmp_path / "logs" / "traffic-collector.log"
        config_path = tmp_path / "config.yml"
        config_path.write_text(
            "max_concurrent_requests: 1\nrequest_timeout_seconds: 5\nmax_consecutive_failures: 2\n",
            encoding="utf-8",
        )
        self.environment = {
            "CONFIG_PATH": str(config_path),
            "SCAN_USERNAME": SCAN_USERNAME,
            "SCAN_PASSWORD": SCAN_PASSWORD,
            "MONGO_HOST": os.environ["MONGO_HOST"],
            "MONGO_PORT": os.environ.get("MONGO_PORT", "27017"),
            "MONGO_USERNAME": os.environ["MONGO_USERNAME"],
            "MONGO_PASSWORD": os.environ["MONGO_PASSWORD"],
            "MONGO_DATABASE": database.name,
            "MONGO_AUTH_SOURCE": os.environ.get("MONGO_AUTH_SOURCE", "admin"),
        }
        self.errors = ""

    def add_interface(
        self, layer: str, name: str, body: str | None, status: int = 200, active: bool = True
    ) -> ObjectId:
        url = self.simulator.serve(f"/{layer}/{name}.log", body or "", status)
        return (
            self.database["interfaces"]
            .insert_one(
                {
                    "layer": layer,
                    "name": name,
                    "scan_url": url,
                    "status": "activa" if active else "desincorporada",
                }
            )
            .inserted_id
        )

    def run(self, force: bool = False) -> ExitCode:
        output, errors = io.StringIO(), io.StringIO()
        exit_code = execute(force, self.environment, TODAY, self.log_path, output, errors)
        self.errors = errors.getvalue()
        return exit_code

    def stored_days(self) -> list[dict]:
        return list(self.database["traffic_daily"].find())

    def log(self) -> str:
        return self.log_path.read_text(encoding="utf-8")


@pytest.fixture
def harness(
    mongo_client: MongoClient, scan_simulator: ScanSimulator, tmp_path: Path
) -> Iterator[Harness]:
    database = mongo_client[f"traffic_collector_flow_{uuid.uuid4().hex[:12]}"]
    yield Harness(database, scan_simulator, tmp_path)
    mongo_client.drop_database(database.name)


def test_complete_run_stores_every_layer_and_exits_zero(harness: Harness) -> None:
    """Every layer is stored with layer and date, and the run exits 0 (RF-016, RF-025, RF-028)."""
    harness.add_interface("BORDE", "a", build_log(288))
    harness.add_interface("DIST", "b", build_log(288))

    assert harness.run() is ExitCode.SUCCESS

    days = harness.stored_days()
    assert sorted(day["layer"] for day in days) == ["BORDE", "DIST"]
    assert {day["date"] for day in days} == {TARGET_DATE}
    assert all(len(day["samples"]) == 288 for day in days)


def test_second_run_without_force_does_not_query_scan(harness: Harness) -> None:
    """A rerun skips collected interfaces, makes no SCAN request and exits 0 (RF-020, RF-028)."""
    harness.add_interface("BORDE", "a", build_log(288))
    harness.add_interface("BORDE", "b", build_log(288))
    assert harness.run() is ExitCode.SUCCESS
    requests_after_first_run = len(harness.simulator.requests)

    assert harness.run() is ExitCode.SUCCESS

    assert len(harness.simulator.requests) == requests_after_first_run
    assert len(harness.stored_days()) == 2


def test_cut_layer_keeps_stored_data_and_next_layer_continues(harness: Harness) -> None:
    """A cut layer keeps what it stored and the next layer still runs (RF-027)."""
    harness.add_interface("A", "ok", build_log(288))
    for name in ("bad1", "bad2", "never1", "never2"):
        harness.add_interface("A", name, "", status=500)
    harness.add_interface("B", "ok", build_log(288))

    exit_code = harness.run()

    assert exit_code is ExitCode.FAILED
    layers_stored = sorted(day["layer"] for day in harness.stored_days())
    assert layers_stored == ["A", "B"]
    assert len([path for path in harness.simulator.requests if path.startswith("/A/")]) <= 3
    assert "cortado por fallas consecutivas" in harness.log()


def test_first_run_generates_the_daily_summary_and_a_rerun_keeps_it(harness: Harness) -> None:
    """The summary is calculated from the stored samples once per interface (RF-026)."""
    interface_id = harness.add_interface("BORDE", "a", build_log(288))

    assert harness.run() is ExitCode.SUCCESS
    assert harness.run() is ExitCode.SUCCESS

    summaries = list(harness.database["traffic_summary_daily"].find())
    assert len(summaries) == 1
    assert summaries[0]["interface_id"] == interface_id
    assert summaries[0]["in_avg"] == pytest.approx(143.5 * 8.022)
    assert summaries[0]["in_max"] == pytest.approx(287 * 8.022)


def test_force_without_valid_new_data_deletes_nothing(harness: Harness) -> None:
    """--force never deletes when SCAN fails; raw and summary stay (RF-021)."""
    interface_id = harness.add_interface("BORDE", "a", build_log(288))
    assert harness.run() is ExitCode.SUCCESS
    harness.database["traffic_summary_daily"].update_one(
        {"interface_id": interface_id, "date": TARGET_DATE}, {"$set": {"in_avg": -1.0}}
    )
    harness.simulator.routes["/BORDE/a.log"] = (500, "")

    exit_code = harness.run(force=True)

    assert exit_code is ExitCode.FAILED
    assert len(harness.stored_days()) == 1
    summaries = list(harness.database["traffic_summary_daily"].find())
    assert [summary["in_avg"] for summary in summaries] == [-1.0]


def test_force_with_new_data_replaces_raw_and_deletes_summary(harness: Harness) -> None:
    """--force replaces the raw day and its summary is recalculated (RF-021, RF-026)."""
    interface_id = harness.add_interface("BORDE", "a", build_log(288))
    assert harness.run() is ExitCode.SUCCESS
    harness.database["traffic_summary_daily"].update_one(
        {"interface_id": interface_id, "date": TARGET_DATE}, {"$set": {"in_avg": -1.0}}
    )
    harness.simulator.routes["/BORDE/a.log"] = (200, build_log(100))

    assert harness.run(force=True) is ExitCode.SUCCESS

    days = harness.stored_days()
    assert len(days) == 1
    assert len(days[0]["samples"]) == 100
    summaries = list(harness.database["traffic_summary_daily"].find())
    assert len(summaries) == 1
    assert summaries[0]["in_max"] == pytest.approx(99 * 8.022)


def test_irregular_log_is_stored_with_warnings(harness: Harness) -> None:
    """287 samples with an invalid line are stored and warned in the log (RF-023, RF-024)."""
    harness.add_interface("BORDE", "a", build_log(287, extra_lines="garbage line\n"))

    assert harness.run() is ExitCode.SUCCESS

    assert len(harness.stored_days()[0]["samples"]) == 287
    assert "287 muestras" in harness.log()
    assert "1 líneas inválidas" in harness.log()


def test_interface_without_valid_samples_fails_and_stores_nothing(harness: Harness) -> None:
    """A log with no valid sample of the day fails the interface (RF-024)."""
    harness.add_interface("BORDE", "a", "garbage\n")

    assert harness.run() is ExitCode.FAILED

    assert harness.stored_days() == []
    assert "sin muestras válidas" in harness.log()


def test_layer_without_active_interfaces_is_skipped_with_warning(harness: Harness) -> None:
    """An empty layer warns and does not stop the run (RF-019)."""
    harness.add_interface("A", "old", None, active=False)
    harness.add_interface("B", "ok", build_log(288))

    assert harness.run() is ExitCode.SUCCESS

    assert "Capa A: sin interfaces activas" in harness.log()


def test_all_layers_empty_exits_with_failure(harness: Harness) -> None:
    """If no layer has active interfaces the exit code is 1 (RF-019, RF-028)."""
    harness.add_interface("A", "old", None, active=False)

    assert harness.run() is ExitCode.FAILED
    assert harness.simulator.requests == []


def test_no_layers_exits_with_process_error_and_no_requests(harness: Harness) -> None:
    """Without layers the process fails with code 2 and never queries SCAN (RF-018, RF-028)."""
    assert harness.run() is ExitCode.PROCESS_ERROR
    assert harness.simulator.requests == []


def test_credentials_never_reach_the_log_or_terminal(harness: Harness) -> None:
    """SCAN and MongoDB passwords stay out of the log and the terminal (RF-029)."""
    harness.add_interface("BORDE", "a", "", status=401)

    harness.run()

    for secret in (SCAN_PASSWORD, os.environ["MONGO_PASSWORD"]):
        assert secret not in harness.log()
        assert secret not in harness.errors
