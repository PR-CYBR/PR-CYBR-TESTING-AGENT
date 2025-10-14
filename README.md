# PR-CYBR-TESTING-AGENT

## Overview
The **PR-CYBR Testing Agent** orchestrates quality signals across the PR-CYBR platform. It continuously evaluates integrations, aggregates telemetry, and coordinates with human operators when automation limits are reached.

## Workflow Architecture
- **Continuous Verification Pipeline:** GitHub Actions workflows dispatch unit, integration, and regression suites on every pull request. Results are published to the shared event bus for downstream consumers.
- **Nightly Synchronization Cycle:** A timed job reconciles test artifacts with the CI/CD, Security, and Performance agents to refresh the cross-agent test matrix and highlight drift.
- **Release Readiness Gate:** Before deployments, the agent validates compliance thresholds, checks open defect SLAs, and signals the Deployment Coordinator via the dashboard webhook.
- **HITL Escalation Loop:** When anomalies exceed automated remediation rules, incident context is handed off to the HITL Response Playbook with live dashboard annotations.

## Automation Hooks
- **`automation_hooks.yml`:** Defines webhook subscriptions for build events, security advisories, and performance regressions.
- **Scripted Utilities:**
  - `./scripts/sync_now.sh` for on-demand synchronization.
  - `./scripts/provision_agent.sh` to bootstrap secrets, dashboards, and shared queues.
  - `./scripts/run_dashboard.sh` to launch the local dashboard experience.
- **Notification Integrations:** Slack and email channels are configured through GitHub Secrets (`SLACK_WEBHOOK_URL`, `STATUS_EMAIL_LIST`).

## Dashboard Usage
- **Command Center:** Displays pass/fail trends, synchronization status, and outstanding escalations.
- **HITL Controls:** Operators can pause automation, rerun specific suites, or attach mitigation notes directly from the dashboard.
- **Widget Library:** Includes test coverage heatmaps, pipeline throughput charts, and cross-agent dependency maps.
- **Audit Trail:** Every override or manual intervention is logged and traceable back to the initiating operator.

## Getting Started
1. **Clone the Repository**
   ```bash
   git clone https://github.com/PR-CYBR/PR-CYBR-TESTING-AGENT.git
   cd PR-CYBR-TESTING-AGENT
   ```
2. **Run Local Setup**
   ```bash
   ./scripts/local_setup.sh
   ```
3. **Provision the Agent**
   ```bash
   ./scripts/provision_agent.sh
   ```
4. **Launch the Dashboard**
   ```bash
   ./scripts/run_dashboard.sh
   ```

## Deployment
- Configure secrets (`CLOUD_API_KEY`, `DOCKERHUB_USERNAME`, `DOCKERHUB_PASSWORD`, `SYNC_API_TOKEN`) in GitHub Actions.
- Push changes to trigger the Docker Compose workflow located in `.github/workflows/docker-compose.yml`.
- Manual deployments are supported through `./scripts/deploy_agent.sh` when cloud CLI access is available.

## Documentation & Support
- Review synchronization details, automation hooks, and dashboard walkthroughs in `docs/README.md`.
- Navigate the broader wiki using `docs/WIKI_MAP.md`.
- Consult `docs/system-diagrams.md` for visual workflow references.

## License
This project is licensed under the **MIT License**. See the [`LICENSE`](LICENSE) file for details.
