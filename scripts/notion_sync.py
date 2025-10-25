"""Utility for synchronising internal data with Notion.

This module exposes a small dispatcher that allows us to route sync
instructions to specific handlers.  A sync "plan" is represented as a list of
objects in the form::

    {"action": "update_page", "payload": {...}}

The dispatcher will call the registered handler with a Notion client and the
provided payload.  When the ``--dry-run`` flag is passed via the CLI the module
will merely log the actions without performing any outbound HTTP requests.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Protocol

import requests

LOGGER = logging.getLogger("notion_sync")


class NotionSyncError(RuntimeError):
    """Raised when the sync process encounters an unrecoverable error."""


class NotionClientProtocol(Protocol):
    """Protocol describing the Notion client features used in this module."""

    def update_page(self, page_id: str, properties: Mapping[str, Any]) -> None:
        ...

    def update_database(self, database_id: str, properties: Mapping[str, Any]) -> None:
        ...


@dataclass
class NotionClient:
    """Minimal HTTP client for the Notion REST API."""

    token: str
    api_version: str = "2022-06-28"

    base_url: str = "https://api.notion.com/v1"

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        headers = kwargs.pop("headers", {})
        session = requests.Session()
        session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": self.api_version,
                "Content-Type": "application/json",
            }
        )
        session.headers.update(headers)
        response = session.request(method, f"{self.base_url}/{endpoint}", **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - passthrough to provide context
            raise NotionSyncError(str(exc)) from exc
        if response.content:
            return response.json()
        return None

    def update_page(self, page_id: str, properties: Mapping[str, Any]) -> None:
        LOGGER.debug("Updating Notion page %s", page_id)
        self._request("patch", f"pages/{page_id}", json={"properties": dict(properties)})

    def update_database(self, database_id: str, properties: Mapping[str, Any]) -> None:
        LOGGER.debug("Updating Notion database %s", database_id)
        self._request("patch", f"databases/{database_id}", json={"properties": dict(properties)})


Handler = Callable[[NotionClientProtocol, Mapping[str, Any]], None]


class NotionSyncDispatcher:
    """Dispatches actions to registered handler callables."""

    def __init__(self, handlers: Optional[Dict[str, Handler]] = None) -> None:
        self._handlers: Dict[str, Handler] = handlers or {}

    def register(self, action: str, handler: Handler) -> None:
        LOGGER.debug("Registering handler for action '%s'", action)
        self._handlers[action] = handler

    def dispatch(
        self,
        action: str,
        client: NotionClientProtocol,
        payload: Mapping[str, Any],
        *,
        dry_run: bool = False,
        logger: Optional[logging.Logger] = None,
    ) -> Dict[str, Any]:
        logger = logger or LOGGER
        if action not in self._handlers:
            raise NotionSyncError(f"No handler registered for action '{action}'")

        if dry_run:
            logger.info("[DRY-RUN] Action '%s' would run with payload: %s", action, json.dumps(payload, sort_keys=True))
            return {"action": action, "payload": dict(payload), "dry_run": True}

        handler = self._handlers[action]
        try:
            handler(client, payload)
        except Exception as exc:  # pragma: no cover - defensive guard
            raise NotionSyncError(f"Handler '{action}' failed") from exc
        return {"action": action, "payload": dict(payload), "dry_run": False}


def update_page_handler(client: NotionClientProtocol, payload: Mapping[str, Any]) -> None:
    page_id = payload.get("page_id")
    properties = payload.get("properties", {})
    if not page_id:
        raise NotionSyncError("'page_id' is required for update_page action")
    client.update_page(page_id, properties)


def update_database_handler(client: NotionClientProtocol, payload: Mapping[str, Any]) -> None:
    database_id = payload.get("database_id")
    properties = payload.get("properties", {})
    if not database_id:
        raise NotionSyncError("'database_id' is required for update_database action")
    client.update_database(database_id, properties)


def build_default_dispatcher() -> NotionSyncDispatcher:
    dispatcher = NotionSyncDispatcher()
    dispatcher.register("update_page", update_page_handler)
    dispatcher.register("update_database", update_database_handler)
    return dispatcher


def load_sync_plan(plan_path: Optional[Path], raw_plan: Optional[str], logger: logging.Logger) -> List[MutableMapping[str, Any]]:
    if raw_plan:
        logger.debug("Loading sync plan from NOTION_SYNC_PLAN environment variable")
        data = json.loads(raw_plan)
    elif plan_path and plan_path.exists():
        logger.debug("Loading sync plan from %s", plan_path)
        with plan_path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    else:
        logger.info("No sync plan provided - nothing to do")
        return []

    if not isinstance(data, Iterable):
        raise NotionSyncError("Sync plan must be an iterable of actions")

    actions: List[MutableMapping[str, Any]] = []
    for idx, item in enumerate(data):
        if not isinstance(item, MutableMapping) or "action" not in item:
            raise NotionSyncError(f"Invalid sync plan entry at index {idx}: {item!r}")
        payload = item.get("payload", {})
        if not isinstance(payload, MutableMapping):
            raise NotionSyncError(f"Payload for action at index {idx} must be a mapping")
        actions.append({"action": item["action"], "payload": dict(payload)})
    return actions


def execute_sync_plan(
    plan: Iterable[Mapping[str, Any]],
    dispatcher: NotionSyncDispatcher,
    client: NotionClientProtocol,
    *,
    dry_run: bool,
    logger: Optional[logging.Logger] = None,
) -> List[Dict[str, Any]]:
    logger = logger or LOGGER
    results: List[Dict[str, Any]] = []
    for item in plan:
        action = item["action"]
        payload = item.get("payload", {})
        logger.debug("Dispatching action '%s'", action)
        result = dispatcher.dispatch(action, client, payload, dry_run=dry_run, logger=logger)
        results.append(result)
    if not plan:
        logger.info("Sync plan was empty - no actions executed")
    return results


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synchronise configuration with Notion")
    parser.add_argument("--plan", type=Path, default=Path("config/notion_sync_plan.json"), help="Path to the sync plan JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Log intended actions without performing API calls")
    parser.add_argument("--log-level", default="INFO", help="Python logging level (default: INFO)")
    return parser.parse_args(list(argv) if argv is not None else None)


def configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    configure_logging(args.log_level)

    raw_plan = os.getenv("NOTION_SYNC_PLAN")
    plan = load_sync_plan(args.plan, raw_plan, LOGGER)

    dispatcher = build_default_dispatcher()

    if args.dry_run:
        client: NotionClientProtocol = DummyClient()
    else:
        token = os.getenv("NOTION_API_TOKEN")
        if not token:
            raise NotionSyncError("NOTION_API_TOKEN environment variable is required for real sync runs")
        client = NotionClient(token=token)

    execute_sync_plan(plan, dispatcher, client, dry_run=args.dry_run, logger=LOGGER)
    return 0


class DummyClient(NotionClientProtocol):
    """Client implementation used during dry-run execution."""

    def update_page(self, page_id: str, properties: Mapping[str, Any]) -> None:  # pragma: no cover - simple logger
        LOGGER.debug("[DRY-RUN CLIENT] update_page(%s, %s)", page_id, properties)

    def update_database(self, database_id: str, properties: Mapping[str, Any]) -> None:  # pragma: no cover - simple logger
        LOGGER.debug("[DRY-RUN CLIENT] update_database(%s, %s)", database_id, properties)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
