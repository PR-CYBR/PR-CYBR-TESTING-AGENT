# Agent Documentation

This document provides information about the agent's functionality, setup, and usage.

## Overview

The PR-CYBR Testing Agent coordinates reliability workstreams across the broader PR-CYBR ecosystem. In addition to local testing capabilities, the agent integrates with external productivity tools to synchronize quality assurance signals and implementation tasks.

## Notion to GitHub Synchronization Design

### Event Ingestion Strategy: Polling vs. Webhooks

| Approach | Advantages | Challenges | Recommended Use |
| --- | --- | --- | --- |
| **Notion Polling** | Simple implementation, no external services required, resilient to transient webhook outages. | Increased API quota consumption, higher latency between Notion updates and GitHub actions, requires scheduled infrastructure. | Fallback mechanism during webhook maintenance windows or when running in air-gapped test environments. |
| **Notion Webhooks** | Near-real-time updates, efficient API usage, first-class support for change payloads. | Requires publicly reachable endpoint or tunnel, additional secret management, webhook signature validation. | Primary integration pattern for production and staging environments. |

**Hybrid Recommendation:** Deploy webhook listeners for production responsiveness while retaining a scheduled polling job (e.g., every 15 minutes) that validates state convergence and backfills missed events.

### Authentication and Secret Management

* Use a dedicated Notion integration token stored in Terraform Cloud workspace variables. The scheduled jobs and webhook services read the token via environment injection; tokens are never committed to source control.
* Rotate the Notion token quarterly and whenever incidents occur. Persist the current token version identifier inside `config/settings.yml` to simplify rollout coordination.
* GitHub access relies on a fine-grained personal access token (classic PATs are discouraged) with `repo` and `issues` scopes only. The token is stored alongside the Notion credentials in Terraform Cloud and surfaced to runtime components through secrets injection.
* All inbound webhook requests must be validated with the Notion signing secret. Reject requests with invalid signatures, stale timestamps, or replayed nonces. Log validation failures with structured metadata for auditability.

## Mapping File and State Tracking

A JSON mapping file (default path: `config/notion_github_mapping.json`) records the relationship between Notion database entries and GitHub issues.

* **Forward Mapping:** Keys are canonical Notion page IDs; values contain GitHub repository, issue number, and sync metadata (e.g., last_synced_at, status hash).
* **Reverse Lookup Support:** Each mapping entry stores the associated GitHub issue node ID so GitHub-originating events can query the file and locate the corresponding Notion record without a linear search. For bulk lookups, index the file into an in-memory dictionary keyed by `issue_id` at service start.
* **State Tracking Fields:** Persist a deterministic hash of critical Notion properties (title, status, assignee) and the last processed Notion `last_edited_time`. During synchronization the agent recomputes the hash; if unchanged, the run skips GitHub API calls to avoid rate-limit churn.
* **Concurrency Controls:** Updates acquire a filesystem lock (e.g., via `fcntl` on Unix) to prevent race conditions between the webhook worker and scheduled polling job. After successful writes, emit a structured log entry and optionally commit the updated mapping back to Git (when operating in infrastructure-as-code mode).

## Future Event Processing Workflow

1. **Webhooks:** Deploy a lightweight FastAPI or AWS Lambda service that exposes `/notion/webhook`. The endpoint verifies signatures, enqueues the payload onto a durable queue (AWS SQS or Redis Streams), and returns 200 immediately.
2. **Scheduled Polling Job:** A GitHub Actions workflow or Terraform-scheduled container runs every 15 minutes. It calls the Notion search API filtered by `last_edited_time` greater than the most recent sync watermark, updating GitHub issues for any deltas.
3. **Queue Consumer:** A worker process (e.g., running under ECS Fargate or GitHub Actions self-hosted runner) consumes webhook payloads, normalizes them into an internal event schema, and invokes the synchronization routines shared with the polling job.
4. **Observability:** Metrics (processed events, API failures, deduplicated updates) are pushed to CloudWatch or Grafana Loki. Alerts trigger when the backlog exceeds thresholds or repeated authentication errors occur.

## GitHub API Interaction Plan

* **Issue Creation:** When a new Notion task with the `Sync to GitHub` property enabled is detected, call `POST /repos/{owner}/{repo}/issues` using the Notion title, map priority to labels, and embed a backlink to Notion in the body. Store the returned `id` and `number` in the mapping file.
* **Issue Updates:**
  * Title or status changes use `PATCH /repos/{owner}/{repo}/issues/{issue_number}`. Translate Notion status (e.g., `In Progress`, `Done`) into GitHub issue state and labels.
  * Comment synchronization leverages `POST /repos/{owner}/{repo}/issues/{issue_number}/comments` when notable Notion discussion updates occur. Include a footer referencing the Notion comment author and timestamp.
* **Issue Closure:** When Notion status transitions to a terminal state (e.g., `Complete`, `Won't Fix`), send `PATCH /repos/{owner}/{repo}/issues/{issue_number}` with `state=closed` and append closure metadata to the issue body. Record the closure timestamp in the mapping file to prevent re-opening.
* **Reopen Logic:** If a closed Notion item reverts to an active status, reopen the GitHub issue with another `PATCH` call (`state=open`) and log the reversal. Update the mapping file's status hash to reflect the new state.
* **Rate Limiting & Backoff:** Wrap all GitHub API interactions in a retry helper that respects secondary rate limits (use exponential backoff with jitter). Capture `X-RateLimit-Remaining` headers and publish metrics to guide future scaling decisions.

## Setup Instructions

(Provide setup instructions here.)

## Usage

(Provide usage instructions here.)
