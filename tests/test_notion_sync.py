import logging
from typing import Mapping

import pytest

from scripts.notion_sync import (
    DummyClient,
    NotionSyncDispatcher,
    NotionSyncError,
    execute_sync_plan,
)


class _RecordingClient(DummyClient):
    def __init__(self) -> None:
        self.page_updates = []
        self.database_updates = []

    def update_page(self, page_id: str, properties: Mapping[str, object]) -> None:
        self.page_updates.append((page_id, dict(properties)))

    def update_database(self, database_id: str, properties: Mapping[str, object]) -> None:
        self.database_updates.append((database_id, dict(properties)))


def test_dispatcher_executes_registered_handler() -> None:
    events = []

    def handler(client, payload):
        events.append((client, payload))

    dispatcher = NotionSyncDispatcher({"example": handler})
    client = object()
    payload = {"foo": "bar"}

    result = dispatcher.dispatch("example", client, payload)

    assert events == [(client, payload)]
    assert result == {"action": "example", "payload": payload, "dry_run": False}


def test_dispatcher_logs_dry_run(caplog) -> None:
    caplog.set_level(logging.INFO)
    dispatcher = NotionSyncDispatcher({"example": lambda c, p: None})

    result = dispatcher.dispatch("example", object(), {"foo": "bar"}, dry_run=True)

    assert "[DRY-RUN] Action 'example'" in caplog.text
    assert result["dry_run"] is True


def test_dispatcher_unknown_action_raises() -> None:
    dispatcher = NotionSyncDispatcher()

    with pytest.raises(NotionSyncError) as exc:
        dispatcher.dispatch("missing", object(), {})

    assert "No handler registered" in str(exc.value)


def test_dispatcher_wraps_handler_errors() -> None:
    def handler(client, payload):
        raise ValueError("boom")

    dispatcher = NotionSyncDispatcher({"explode": handler})

    with pytest.raises(NotionSyncError) as exc:
        dispatcher.dispatch("explode", object(), {})

    assert "Handler 'explode' failed" in str(exc.value)


def test_execute_sync_plan_invokes_handlers_in_order() -> None:
    dispatcher = NotionSyncDispatcher()
    client = _RecordingClient()

    dispatcher.register("update_page", lambda client, payload: client.update_page(payload["page_id"], payload["properties"]))
    dispatcher.register(
        "update_database",
        lambda client, payload: client.update_database(payload["database_id"], payload["properties"]),
    )

    plan = [
        {"action": "update_page", "payload": {"page_id": "abc", "properties": {"Status": {"select": {"name": "Live"}}}}},
        {
            "action": "update_database",
            "payload": {"database_id": "db1", "properties": {"Name": {"title": [{"text": {"content": "Item"}}]}}},
        },
    ]

    results = execute_sync_plan(plan, dispatcher, client, dry_run=False, logger=logging.getLogger("test"))

    assert client.page_updates == [("abc", {"Status": {"select": {"name": "Live"}}})]
    assert client.database_updates == [
        ("db1", {"Name": {"title": [{"text": {"content": "Item"}}]}})
    ]
    assert [item["action"] for item in results] == ["update_page", "update_database"]
