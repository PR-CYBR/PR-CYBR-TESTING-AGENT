# Notion Integration Playbook

## Overview
This document outlines how the PR-CYBR testing agent synchronises metadata with
Notion. The integration uses a scripted dispatcher (`scripts/notion_sync.py`)
to coordinate specific update operations such as page and database property
updates. Sync plans are provided as JSON either through the
`config/notion_sync_plan.json` file or the `NOTION_SYNC_PLAN` environment
variable.

## Branching Expectations
* All integration updates must be staged from a dedicated feature branch off of
  `work`; avoid committing directly to `main` so the CI/CD automation from the
  spec-bootstrap baseline remains intact.
* Merge to `work` only after validation and peer review. Promotion from `work`
  to production branches follows the standard release cadence managed in
  Terraform Cloud.

## Testing Strategy
1. Create or update a sync plan and run `python scripts/notion_sync.py --dry-run`
   locally. The dry run ensures handlers receive the expected payload without
   performing API calls.
2. Execute `pytest` to validate dispatcher routing and error handling logic.
3. Confirm the GitHub Action `Notion Sync` workflow succeeds in CI; it runs
   `pytest` before invoking the sync script to guarantee the code is tested
   prior to any live API interaction.

## GitHub Action Tokens
* The `Notion Sync` workflow requests the minimal required GitHub token
  permissions (`contents: read`) to fetch repository content only.
* Avoid granting write or administrative scopes to the workflow. Store the
  Notion token in GitHub secrets and load it only for the step that performs the
  real sync.

## Notion Integration Permissions
* Provision the Notion integration with the narrowest access scope possible—
  restrict it to only the databases and pages referenced by the sync plan.
* Revoke database or page access that is no longer required and rotate tokens
  if unused for more than 90 days.
* Monitor Notion's integration activity log after each sync and configure alerts
  on unexpected changes via Notion's admin dashboard.

## Monitoring & Incident Response
* After each workflow run, review the step summary in GitHub Actions to confirm
  whether it was a dry run or a live update. Dry runs log the intended actions
  while live runs log the API endpoints targeted.
* Enable repository branch protection rules to ensure PR reviews precede any
  workflow dispatch with live credentials.
* Maintain a Terraform Cloud variable set that holds the secrets used in the
  workflow so they can be rotated centrally without updating the repository.
