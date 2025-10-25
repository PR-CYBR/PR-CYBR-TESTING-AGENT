#!/usr/bin/env python3
"""Synchronise GitHub events to Notion databases.

This script provides a command line interface that can process individual
or batched GitHub webhook payloads and upsert the relevant information into
Notion databases. The script is designed to be resilient – failures in one
event do not stop subsequent events from being processed – and persists the
relationship between GitHub entities and Notion pages for future updates.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from notion_client import Client, APIResponseError


BASE_DIR = Path(__file__).resolve().parents[1]
MAPPINGS_PATH = BASE_DIR / "config" / "notion_mappings.json"

# Map GitHub event types to the environment variables containing the Notion
# database identifiers. A default database can be provided via
# ``NOTION_DEFAULT_DATABASE_ID`` when a more specific mapping is not set.
DATABASE_ENV_VARS: Mapping[str, str] = {
    "issues": "NOTION_ISSUE_DATABASE_ID",
    "pull_request": "NOTION_PULL_REQUEST_DATABASE_ID",
    "discussion": "NOTION_DISCUSSION_DATABASE_ID",
    "project": "NOTION_PROJECT_DATABASE_ID",
    "workflow_run": "NOTION_WORKFLOW_DATABASE_ID",
}
DEFAULT_DATABASE_ENV = "NOTION_DEFAULT_DATABASE_ID"


class JsonFormatter(logging.Formatter):
    """Render log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - see class docstring
        payload = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        for attr in ("event_type", "github_id", "notion_id", "mapping_key"):
            value = getattr(record, attr, None)
            if value is not None:
                payload[attr] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    """Configure JSON structured logging for the script."""

    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            handler.setLevel(level.upper())
        return

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.setLevel(level.upper())
    root_logger.addHandler(handler)
    root_logger.setLevel(level.upper())


def load_mappings(path: Path = MAPPINGS_PATH) -> MutableMapping[str, str]:
    """Load persisted GitHub ↔ Notion mappings."""

    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except json.JSONDecodeError:
        logging.getLogger(__name__).warning(
            "Failed to decode JSON mappings, starting with empty cache",
            extra={"path": str(path)},
        )
        return {}


def atomic_write_json(data: Mapping[str, str], path: Path = MAPPINGS_PATH) -> None:
    """Persist JSON data atomically to avoid partial writes."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as tmp_fp:
        json.dump(data, tmp_fp, ensure_ascii=False, indent=2, sort_keys=True)
        tmp_fp.flush()
        os.fsync(tmp_fp.fileno())
    temp_path.replace(path)


def ensure_database_id(event_type: str, env: Mapping[str, str]) -> Optional[str]:
    """Retrieve the Notion database ID for the given event type."""

    specific_env = DATABASE_ENV_VARS.get(event_type)
    if specific_env:
        db_id = env.get(specific_env)
        if db_id:
            return db_id
    return env.get(DEFAULT_DATABASE_ENV)


def notion_rich_text(content: str) -> List[Dict[str, Any]]:
    """Create a Notion rich text block, truncating when necessary."""

    if len(content) > 1900:
        content = f"{content[:1897]}..."
    return [{"type": "text", "text": {"content": content}}]


def build_common_properties(
    title: str,
    url: Optional[str],
    state: Optional[str],
    updated_at: Optional[str],
    metadata: Optional[Mapping[str, Any]],
    *,
    type_name: Optional[str] = None,
    number: Optional[int] = None,
) -> Dict[str, Any]:
    """Construct a dictionary of Notion page properties shared across handlers."""

    properties: Dict[str, Any] = {
        "Name": {"title": notion_rich_text(title or "Untitled")},
    }
    if url:
        properties["URL"] = {"url": url}
    if state:
        properties["State"] = {"select": {"name": state.title() if state else "Unknown"}}
    if updated_at:
        properties["Last Updated"] = {"date": {"start": updated_at}}
    if metadata:
        properties["Metadata"] = {"rich_text": notion_rich_text(json.dumps(metadata, ensure_ascii=False, sort_keys=True))}
    if type_name:
        properties["Type"] = {"select": {"name": type_name}}
    if number is not None:
        properties["Number"] = {"number": number}
    return properties


def make_mapping_key(event_type: str, github_id: Any) -> str:
    """Create a unique mapping key for a GitHub entity."""

    return f"{event_type}:{github_id}"


def entity_identifier(entity: Mapping[str, Any]) -> Any:
    """Return the most stable identifier available on a GitHub payload."""

    return (
        entity.get("node_id")
        or entity.get("id")
        or entity.get("number")
        or entity.get("name")
    )


@dataclass
class NotionSyncContext:
    """Runtime state shared across event handlers."""

    client: Client
    mappings: MutableMapping[str, str]
    env: Mapping[str, str]

    def upsert_page(
        self,
        event_type: str,
        github_id: Any,
        properties: Mapping[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """Create or update a Notion page and update the mapping cache."""

        logger = logging.getLogger(__name__)
        database_id = ensure_database_id(event_type, self.env)
        if not database_id:
            logger.error(
                "Missing Notion database ID for event type",
                extra={"event_type": event_type, "github_id": github_id},
            )
            return False, None

        mapping_key = make_mapping_key(event_type, github_id)
        notion_id = self.mappings.get(mapping_key)
        try:
            if notion_id:
                self.client.pages.update(page_id=notion_id, properties=properties)
                logger.info(
                    "Updated Notion page",
                    extra={
                        "event_type": event_type,
                        "github_id": github_id,
                        "notion_id": notion_id,
                        "mapping_key": mapping_key,
                    },
                )
                return False, notion_id
            response = self.client.pages.create(
                parent={"database_id": database_id},
                properties=dict(properties),
            )
            notion_id = response.get("id")
            if notion_id:
                self.mappings[mapping_key] = notion_id
            logger.info(
                "Created Notion page",
                extra={
                    "event_type": event_type,
                    "github_id": github_id,
                    "notion_id": notion_id,
                    "mapping_key": mapping_key,
                },
            )
            return True, notion_id
        except APIResponseError as exc:  # pragma: no cover - network dependent
            logger.error(
                "Notion API error",
                extra={
                    "event_type": event_type,
                    "github_id": github_id,
                    "notion_id": notion_id,
                    "mapping_key": mapping_key,
                },
                exc_info=exc,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(
                "Unexpected error when upserting page",
                extra={
                    "event_type": event_type,
                    "github_id": github_id,
                    "notion_id": notion_id,
                    "mapping_key": mapping_key,
                },
                exc_info=exc,
            )
        return False, notion_id


def handle_issues(event_payload: Mapping[str, Any], context: NotionSyncContext) -> bool:
    issue = event_payload.get("issue", {})
    github_id = entity_identifier(issue)
    if github_id is None:
        logging.getLogger(__name__).warning("Issue payload missing identifier")
        return False

    metadata = {
        "author": issue.get("user", {}).get("login"),
        "assignees": [assignee.get("login") for assignee in issue.get("assignees", [])],
        "labels": [label.get("name") for label in issue.get("labels", [])],
    }
    properties = build_common_properties(
        title=issue.get("title", ""),
        url=issue.get("html_url"),
        state=issue.get("state"),
        updated_at=issue.get("updated_at"),
        metadata=metadata,
        number=issue.get("number"),
        type_name="Issue",
    )
    changed, _ = context.upsert_page("issues", github_id, properties)
    return changed


def handle_pull_request(event_payload: Mapping[str, Any], context: NotionSyncContext) -> bool:
    pr = event_payload.get("pull_request", {})
    github_id = entity_identifier(pr)
    if github_id is None:
        logging.getLogger(__name__).warning("Pull request payload missing identifier")
        return False

    state = "merged" if pr.get("merged") else pr.get("state")
    metadata = {
        "author": pr.get("user", {}).get("login"),
        "merged": pr.get("merged"),
        "mergeable": pr.get("mergeable"),
        "reviewers": [reviewer.get("login") for reviewer in pr.get("requested_reviewers", [])],
    }
    properties = build_common_properties(
        title=pr.get("title", ""),
        url=pr.get("html_url"),
        state=state,
        updated_at=pr.get("updated_at"),
        metadata=metadata,
        number=pr.get("number"),
        type_name="Pull Request",
    )
    changed, _ = context.upsert_page("pull_request", github_id, properties)
    return changed


def handle_discussion(event_payload: Mapping[str, Any], context: NotionSyncContext) -> bool:
    discussion = event_payload.get("discussion", {})
    github_id = entity_identifier(discussion)
    if github_id is None:
        logging.getLogger(__name__).warning("Discussion payload missing identifier")
        return False

    metadata = {
        "author": discussion.get("user", {}).get("login"),
        "category": discussion.get("category", {}).get("name"),
        "answer_chosen": discussion.get("answer_chosen"),
    }
    properties = build_common_properties(
        title=discussion.get("title", ""),
        url=discussion.get("html_url"),
        state=discussion.get("state"),
        updated_at=discussion.get("updated_at"),
        metadata=metadata,
        type_name="Discussion",
    )
    changed, _ = context.upsert_page("discussion", github_id, properties)
    return changed


def handle_project(event_payload: Mapping[str, Any], context: NotionSyncContext) -> bool:
    project = event_payload.get("project", {})
    github_id = entity_identifier(project)
    if github_id is None:
        logging.getLogger(__name__).warning("Project payload missing identifier")
        return False

    metadata = {
        "body": project.get("body"),
        "creator": project.get("creator", {}).get("login"),
    }
    properties = build_common_properties(
        title=project.get("name", ""),
        url=project.get("html_url"),
        state=project.get("state"),
        updated_at=project.get("updated_at"),
        metadata=metadata,
        type_name="Project",
    )
    changed, _ = context.upsert_page("project", github_id, properties)
    return changed


def handle_workflow_run(event_payload: Mapping[str, Any], context: NotionSyncContext) -> bool:
    workflow = event_payload.get("workflow_run", {})
    github_id = entity_identifier(workflow)
    if github_id is None:
        logging.getLogger(__name__).warning("Workflow run payload missing identifier")
        return False

    state = workflow.get("conclusion") or workflow.get("status")
    metadata = {
        "workflow_name": workflow.get("name"),
        "run_attempt": workflow.get("run_attempt"),
        "status": workflow.get("status"),
        "conclusion": workflow.get("conclusion"),
    }
    properties = build_common_properties(
        title=workflow.get("display_title") or workflow.get("name") or "Workflow Run",
        url=workflow.get("html_url"),
        state=state,
        updated_at=workflow.get("updated_at"),
        metadata=metadata,
        type_name="Workflow",
    )
    changed, _ = context.upsert_page("workflow_run", github_id, properties)
    return changed


EVENT_HANDLERS = {
    "issues": handle_issues,
    "issue": handle_issues,
    "pull_request": handle_pull_request,
    "pull_request_target": handle_pull_request,
    "discussion": handle_discussion,
    "project": handle_project,
    "workflow_run": handle_workflow_run,
}


def iter_events(
    payload: Any, default_event_type: Optional[str]
) -> Iterable[Tuple[str, Mapping[str, Any]]]:
    """Yield ``(event_type, payload)`` tuples from the provided data."""

    if isinstance(payload, list):
        for event in payload:
            if not isinstance(event, Mapping):
                raise ValueError("Each event entry must be an object")
            event_type = event.get("event_type") or default_event_type
            if not event_type:
                raise ValueError("Event type missing for one of the payload entries")
            yield event_type, event
        return

    if not isinstance(payload, Mapping):
        raise ValueError("Payload must be a JSON object or an array of objects")

    event_type = payload.get("event_type") or default_event_type
    if not event_type:
        raise ValueError("Event type is required when it cannot be inferred from payload")
    yield event_type, payload


def dispatch_events(
    events: Iterable[Tuple[str, Mapping[str, Any]]],
    context: NotionSyncContext,
) -> None:
    """Dispatch events to their handlers with resilience to per-event failures."""

    logger = logging.getLogger(__name__)
    for event_type, payload in events:
        handler = EVENT_HANDLERS.get(event_type)
        if handler is None:
            logger.warning("No handler registered for event type", extra={"event_type": event_type})
            continue

        try:
            changed = handler(payload, context)
            if changed:
                atomic_write_json(context.mappings)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(
                "Failed to process event",
                extra={"event_type": event_type},
                exc_info=exc,
            )


def parse_arguments(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--event-type",
        dest="event_type",
        help=(
            "Optional GitHub event type. If omitted, each payload entry must include an "
            "'event_type' field."
        ),
        choices=sorted(EVENT_HANDLERS.keys()),
    )
    parser.add_argument(
        "--payload-file",
        dest="payload_file",
        type=Path,
        help=(
            "Path to the JSON payload file. If omitted, the script reads from standard input."
        ),
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default=os.environ.get("NOTION_SYNC_LOG_LEVEL", "INFO"),
        help="Logging level (default: INFO or NOTION_SYNC_LOG_LEVEL).",
    )
    return parser.parse_args(argv)


def load_payload(path: Optional[Path]) -> Any:
    if path is None:
        data = json.load(os.fdopen(os.dup(0), "r", encoding="utf-8"))
    else:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    return data


def create_client(token: str) -> Client:
    return Client(auth=token)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_arguments(argv)
    configure_logging(args.log_level)
    logger = logging.getLogger(__name__)

    token = os.environ.get("NOTION_TOKEN")
    if not token:
        logger.error("NOTION_TOKEN environment variable is required")
        return 1

    try:
        payload = load_payload(args.payload_file)
    except Exception as exc:
        logger.error("Unable to load payload", exc_info=exc)
        return 1

    try:
        events = list(iter_events(payload, args.event_type))
    except Exception as exc:
        logger.error("Invalid payload", exc_info=exc)
        return 1

    context = NotionSyncContext(
        client=create_client(token),
        mappings=load_mappings(),
        env=os.environ,
    )

    dispatch_events(events, context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

