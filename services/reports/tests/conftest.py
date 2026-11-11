import os
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

from reports.constants.constants import CARACAS_TIMEZONE
from tests.fakes import FixedClock

MONGO_ENVIRONMENT = {
    "MONGO_HOST": "mongo",
    "MONGO_PORT": "27017",
    "MONGO_USERNAME": "user",
    "MONGO_PASSWORD": "secret-password",
    "MONGO_DATABASE": "scan_backup",
}


@pytest.fixture
def clock() -> FixedClock:
    """Clock fixed at 2026-11-10 15:30:00 in America/Caracas."""
    return FixedClock(datetime(2026, 11, 10, 15, 30, 0, tzinfo=CARACAS_TIMEZONE))


@pytest.fixture
def export_directory(tmp_path: Path) -> Path:
    """An existing, writable export directory."""
    directory = tmp_path / "exports"
    directory.mkdir()
    return directory


@pytest.fixture(scope="session")
def mongo_client() -> Iterator[MongoClient]:
    """A client to the MongoDB of the environment; the test is skipped if it is unreachable."""
    required = ("MONGO_HOST", "MONGO_USERNAME", "MONGO_PASSWORD")
    if any(not os.environ.get(name) for name in required):
        pytest.skip("MongoDB environment variables are not set")
    client: MongoClient = MongoClient(
        host=os.environ["MONGO_HOST"],
        port=int(os.environ.get("MONGO_PORT", "27017")),
        username=os.environ["MONGO_USERNAME"],
        password=os.environ["MONGO_PASSWORD"],
        authSource=os.environ.get("MONGO_AUTH_SOURCE", "admin"),
        serverSelectionTimeoutMS=2000,
        tz_aware=True,
    )
    try:
        client.admin.command("ping")
    except PyMongoError:
        client.close()
        pytest.skip("MongoDB is not reachable")
    yield client
    client.close()


@pytest.fixture
def database(mongo_client: MongoClient) -> Iterator[Database]:
    """A throwaway database, dropped after the test; `MONGO_DATABASE` is never touched."""
    test_database = mongo_client[f"reports_test_{uuid4().hex[:12]}"]
    yield test_database
    mongo_client.drop_database(test_database.name)
