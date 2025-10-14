"""Dashboard API for workflow orchestration, analytics, and live status feeds.

This module exposes a FastAPI application that can be mounted inside the
project's existing web server or launched standalone with ``uvicorn``.
The API keeps an in-memory representation of the active workflows, their
execution metadata, and recent log messages that form a live activity feed.

Example
-------
    from dashboard.dashboard_api import api
    import uvicorn

    if __name__ == "__main__":
        uvicorn.run(api.app, host="0.0.0.0", port=8000)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Iterable, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class WorkflowStatus(str, Enum):
    """Lifecycle states tracked for each workflow."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"


@dataclass
class Workflow:
    """Internal representation of an orchestrated workflow."""

    workflow_id: str
    name: str
    status: WorkflowStatus = WorkflowStatus.IDLE
    runs: int = 0
    last_run: Optional[datetime] = None
    owner: str = "operations"
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        """Serialize the workflow into an API-safe payload."""

        return {
            "id": self.workflow_id,
            "name": self.name,
            "status": self.status.value,
            "runs": self.runs,
            "lastRun": self.last_run.isoformat() if self.last_run else None,
            "owner": self.owner,
            "tags": self.tags,
        }


@dataclass
class LogEvent:
    """Captured log message for the live activity feed."""

    workflow_id: str
    level: str
    message: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, object]:
        return {
            "workflowId": self.workflow_id,
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp.replace(tzinfo=timezone.utc).isoformat(),
            "epoch": self.timestamp.timestamp(),
        }


class WorkflowAction(str, Enum):
    """Supported orchestration actions."""

    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"


class ActionRequest(BaseModel):
    action: WorkflowAction


class DashboardAPI:
    """Encapsulates the FastAPI app and the orchestration state."""

    def __init__(self) -> None:
        self.app = FastAPI(title="Agent Workflow Dashboard", version="1.0.0")
        self._workflows: Dict[str, Workflow] = {}
        self._log_feed: List[LogEvent] = []
        self._bootstrap_sample_data()
        self._configure_routes()
        self._configure_cors()

    # ------------------------------------------------------------------
    # Configuration helpers
    def _configure_cors(self) -> None:
        """Allow local dashboard clients to call the API."""

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _configure_routes(self) -> None:
        """Register all REST endpoints with FastAPI."""

        @self.app.get("/api/workflows")
        def list_workflows() -> Dict[str, Iterable[Dict[str, object]]]:
            """Return every known workflow with metadata."""

            return {"workflows": [wf.to_dict() for wf in self._workflows.values()]}

        @self.app.get("/api/workflows/{workflow_id}")
        def get_workflow(workflow_id: str) -> Dict[str, object]:
            workflow = self._require_workflow(workflow_id)
            return workflow.to_dict()

        @self.app.post("/api/workflows/{workflow_id}/actions")
        def orchestrate_workflow(workflow_id: str, request: ActionRequest) -> Dict[str, object]:
            workflow = self._require_workflow(workflow_id)
            self._apply_action(workflow, request.action)
            return {"workflow": workflow.to_dict()}

        @self.app.get("/api/workflows/{workflow_id}/logs")
        def workflow_logs(workflow_id: str, limit: int = Query(50, ge=1, le=500)) -> Dict[str, Iterable[Dict[str, object]]]:
            self._require_workflow(workflow_id)
            logs = [event for event in self._log_feed if event.workflow_id == workflow_id]
            return {"logs": [event.to_dict() for event in logs[-limit:]]}

        @self.app.get("/api/analytics/summary")
        def analytics_summary() -> Dict[str, object]:
            metrics = self._build_analytics()
            return {"analytics": metrics}

        @self.app.get("/api/status/live")
        def live_status_feed(since: float = Query(0.0, ge=0.0)) -> Dict[str, object]:
            """Return log events after the provided epoch timestamp."""

            events = [event for event in self._log_feed if event.timestamp.timestamp() > since]
            next_marker = self._log_feed[-1].timestamp.timestamp() if self._log_feed else since
            return {
                "events": [event.to_dict() for event in events],
                "nextSince": next_marker,
            }

    def _bootstrap_sample_data(self) -> None:
        """Populate the dashboard with mock workflows and log lines."""

        now = datetime.now(timezone.utc)
        workflows = [
            Workflow("data_ingest", "Data Ingestion", WorkflowStatus.RUNNING, runs=12, last_run=now, tags=["etl", "hourly"]),
            Workflow("model_train", "Model Training", WorkflowStatus.IDLE, runs=5, last_run=now, tags=["ml"]),
            Workflow("report_gen", "Report Generation", WorkflowStatus.PAUSED, runs=30, last_run=now, tags=["reporting"]),
        ]
        for wf in workflows:
            self._workflows[wf.workflow_id] = wf

        self._log_feed.extend(
            [
                LogEvent("data_ingest", "INFO", "Ingestion pipeline started", now),
                LogEvent("data_ingest", "INFO", "Received 10k records", now),
                LogEvent("model_train", "WARNING", "Model accuracy below threshold", now),
                LogEvent("report_gen", "INFO", "Report generator paused awaiting approval", now),
            ]
        )

    # ------------------------------------------------------------------
    # Internal utilities
    def _require_workflow(self, workflow_id: str) -> Workflow:
        try:
            return self._workflows[workflow_id]
        except KeyError as exc:  # pragma: no cover - defensive branch
            raise HTTPException(status_code=404, detail="Workflow not found") from exc

    def _apply_action(self, workflow: Workflow, action: WorkflowAction) -> None:
        now = datetime.now(timezone.utc)
        message: Optional[str] = None

        if action is WorkflowAction.START:
            if workflow.status is WorkflowStatus.RUNNING:
                raise HTTPException(status_code=400, detail="Workflow already running")
            workflow.status = WorkflowStatus.RUNNING
            workflow.runs += 1
            workflow.last_run = now
            message = "Workflow started"
        elif action is WorkflowAction.RESUME:
            if workflow.status not in {WorkflowStatus.PAUSED, WorkflowStatus.FAILED}:
                raise HTTPException(status_code=400, detail="Workflow cannot be resumed from current state")
            workflow.status = WorkflowStatus.RUNNING
            message = "Workflow resumed"
        elif action is WorkflowAction.PAUSE:
            if workflow.status is not WorkflowStatus.RUNNING:
                raise HTTPException(status_code=400, detail="Workflow is not running")
            workflow.status = WorkflowStatus.PAUSED
            message = "Workflow paused"
        elif action is WorkflowAction.STOP:
            if workflow.status in {WorkflowStatus.IDLE, WorkflowStatus.COMPLETED}:
                raise HTTPException(status_code=400, detail="Workflow already stopped")
            workflow.status = WorkflowStatus.COMPLETED
            message = "Workflow stopped"

        if message:
            self._log_feed.append(
                LogEvent(
                    workflow.workflow_id,
                    "INFO",
                    message,
                    now,
                )
            )

    def _build_analytics(self) -> Dict[str, object]:
        """Aggregate analytics for the dashboard."""

        total_runs = sum(workflow.runs for workflow in self._workflows.values())
        running = sum(1 for workflow in self._workflows.values() if workflow.status is WorkflowStatus.RUNNING)
        paused = sum(1 for workflow in self._workflows.values() if workflow.status is WorkflowStatus.PAUSED)
        failed = sum(1 for workflow in self._workflows.values() if workflow.status is WorkflowStatus.FAILED)

        return {
            "totalRuns": total_runs,
            "running": running,
            "paused": paused,
            "failed": failed,
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
        }


api = DashboardAPI()
"""Module-level API singleton that can be imported directly."""

app: FastAPI = api.app
"""Convenience alias for ASGI servers."""
