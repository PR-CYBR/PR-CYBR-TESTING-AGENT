# Agent Documentation

This documentation suite outlines how the PR-CYBR Testing Agent synchronizes with peer agents, exposes automation hooks, and surfaces operational telemetry through the shared dashboard.

## Synchronization Blueprint
- **Cadence Alignment:** Nightly reconciliation jobs pull state from CI/CD, security, and performance agents to refresh the unified test matrix.
- **Data Contracts:** JSON schemas in `config/contracts/` ensure result payloads remain consistent across agents.
- **HITL Overrides:** Human-in-the-loop responders can pause or resume automated test plans via the `agent-dashboard`'s override controls.
- **Escalation Ladders:** Critical defects route to the Security Agent first, then escalate to the HITL playbook if remediation exceeds four hours.

## Dashboard Overview
- **Operational Snapshot:** The dashboard home view highlights pass/fail ratios, open defects, and synchronization drift indicators.
- **Widget Catalog:** Deployable widgets include test coverage heatmaps, integration queue depth, and agent health status.
- **Alerting & Notifications:** Configurable thresholds trigger Slack and email notifications through the `automation_hooks.yml` definitions.
- **HITL Console:** Operators can annotate anomalous runs, attach mitigation notes, and promote fixes into the backlog.

## Cross-Agent Links
- **CI/CD Agent Workflows:** Shares pipeline verdicts and deployment readiness gates.
- **Security Agent Integrations:** Supplies vulnerability scans for gating releases and calibrating test severity.
- **Performance Agent Feedback:** Injects load profiles and regression metrics to guide scenario prioritization.
- **Knowledge Base:** See `docs/WIKI_MAP.md` for the authoritative cross-agent link map.

## Setup Instructions
1. Install dependencies via `./scripts/local_setup.sh`.
2. Configure synchronization secrets (`SYNC_API_TOKEN`, `DASHBOARD_API_KEY`) in your environment.
3. Run `./scripts/provision_agent.sh` to register automation hooks.

## Usage
- Launch the dashboard with `./scripts/run_dashboard.sh` and authenticate using your assigned API key.
- Trigger an ad-hoc synchronization cycle using `./scripts/sync_now.sh`.
- Review system diagrams in `docs/system-diagrams.md` to understand workflow interconnections and HITL touchpoints.
