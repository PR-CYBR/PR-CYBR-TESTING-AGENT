# Terraform Cloud Workflow Bridge

_Last updated: 2025-10-26_

## Overview

This repository uses the [Terraform Cloud workflow bridge](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/github-app/workflow-bridge) pattern so that GitHub Actions only orchestrates runs while Terraform Cloud retains ownership of all sensitive state and environment variables.

Two GitHub Actions workflows manage the integration:

- `.github/workflows/tfc-speculative-run.yml` uploads the current configuration and triggers a speculative plan for pull requests that target `main`.
- `.github/workflows/tfc-apply-run.yml` promotes merged changes by triggering an apply run after commits land on `main`.

Both workflows rely on repository variables and secrets to determine how to contact Terraform Cloud. Once the run is started, Terraform Cloud uses its workspace variables to supply all provider credentials, service tokens, and any other sensitive values.

## Required configuration

Add the following repository-level values so the workflows can contact the correct Terraform Cloud workspace:

| Type     | Name                     | Purpose                                                    |
|----------|--------------------------|------------------------------------------------------------|
| Variable | `TF_CLOUD_ORGANIZATION`  | Terraform Cloud organization that owns the workspace.      |
| Variable | `TF_WORKSPACE`           | Terraform Cloud workspace name (e.g., `pr-cybr-testing`).  |
| Variable | `TF_CONFIG_DIRECTORY`    | Relative path to the Terraform configuration (defaults to `.` when left blank). |
| Secret   | `TFC_API_TOKEN`          | Terraform Cloud user or team API token with permission to upload configurations and create runs. |

> **Tip:** Keep provider credentials and other environment secrets in the Terraform Cloud workspace. Only the API token above needs to live in GitHub so that the workflow can authenticate.

## Pull request experience

1. Developers open a pull request against `main`.
2. `tfc-speculative-run` uploads the configuration located in `TF_CONFIG_DIRECTORY` and starts a speculative run in Terraform Cloud.
3. When the run finishes, the workflow comments on the pull request with the add/change/destroy summary and a deep link to the run details.
4. If the run fails or requires intervention, the job fails so reviewers can address the issue before merging.

> Pull requests from forked repositories skip the Terraform Cloud workflow because GitHub does not expose secrets to forked workflows.

## Apply workflow

1. After a pull request merges, a push to `main` triggers `tfc-apply-run`.
2. The workflow re-uploads the configuration for provenance, creates a run, and automatically confirms the apply if Terraform Cloud indicates confirmation is required.
3. The job logs the Terraform Cloud run URL so operators can follow progress in the UI.

If Terraform Cloud cannot create a run or returns an error, the workflow fails and surfaces the run status in the job logs.

## Extending the workflows

- Adjust the `paths` filters in each workflow if additional files should trigger Terraform runs.
- Update the branch filters to mirror the promotion model defined for this repository.
- Add extra steps (for example, `plan-output` or `show-run`) if you want to capture more metadata in the GitHub summary.

Because Terraform Cloud retains all environment variables and secrets, these workflows keep sensitive information out of GitHub while still providing an auditable change trail.
