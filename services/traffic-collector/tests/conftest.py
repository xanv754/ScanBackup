import os
import uuid
from collections.abc import Iterator

import pytest
from pymongo import MongoClient, monitoring
from pymongo.database import Database
from pymongo.errors import PyMongoError

CONNECTION_TIMEOUT_MS = 2000


class CommandRecorder(monitoring.CommandListener):
    """Keeps the name and collection of every command sent to MongoDB."""

    def __init__(self) -> None:
        self.commands: list[tuple[str, str]] = []

    def started(self, event: monitoring.CommandStartedEvent) -> None:
        self.commands.append(
            (event.command_name, str(event.command.get(event.command_name)))
        )

    def succeeded(self, event: monitoring.CommandSucceededEvent) -> None:
        return

    def failed(self, event: monitoring.CommandFailedEvent) -> None:
        return

    def count(self, command_name: str, collection: str) -> int:
        return self.commands.count((command_name, collection))


@pytest.fixture(scope="session")
def command_recorder() -> CommandRecorder:
    return CommandRecorder()


@pytest.fixture(scope="session")
def mongo_client(command_recorder: CommandRecorder) -> Iterator[MongoClient]:
    """Client to the development MongoDB, taken from the MONGO_* variables; skips if absent."""
    host = os.environ.get("MONGO_HOST")
    username = os.environ.get("MONGO_USERNAME")
    password = os.environ.get("MONGO_PASSWORD")
    if not (host and username and password):
        pytest.skip("MongoDB environment variables are not set")
    client = MongoClient(
        host=host,
        port=int(os.environ.get("MONGO_PORT", "27017")),
        username=username,
        password=password,
        authSource=os.environ.get("MONGO_AUTH_SOURCE", "admin"),
        serverSelectionTimeoutMS=CONNECTION_TIMEOUT_MS,
        tz_aware=True,
        event_listeners=[command_recorder],
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
    """A throwaway database in the development server, dropped after the test."""
    name = f"traffic_collector_test_{uuid.uuid4().hex[:12]}"
    yield mongo_client[name]
    mongo_client.drop_database(name)
