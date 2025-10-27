# A-06 Testing Agent Terraform Schema

_Last updated: 2025-04-28_

## Workspace Variable Inventory
The Terraform Cloud workspace for A-06 is expected to provide the following variables. Sensitive values are delivered via TFC environment variables and never stored in this repository.

| Variable | Sensitivity | Purpose |
| --- | --- | --- |
| `AGENT_ACTIONS` | Sensitive | Grants GitHub Actions runners access to CI-managed resources. |
| `NOTION_DISCUSSIONS_ARC_DB_ID` | Non-sensitive | Routes architecture discussion updates to the correct Notion database. |
| `NOTION_ISSUES_BACKLOG_DB_ID` | Non-sensitive | Identifies the Notion issues backlog database. |
| `NOTION_KNOWLEDGE_FILE_DB_ID` | Non-sensitive | Identifies the Notion knowledge files database. |
| `NOTION_PAGE_ID` | Non-sensitive | Points to the root Notion page for the testing agent. |
| `NOTION_PR_BACKLOG_DB_ID` | Non-sensitive | Identifies the Notion PR backlog database. |
| `NOTION_PROJECT_BOARD_BACKLOG_DB_ID` | Non-sensitive | Identifies the Notion project board backlog database. |
| `NOTION_TASK_BACKLOG_DB_ID` | Non-sensitive | Identifies the Notion task backlog database. |
| `NOTION_TOKEN` | Sensitive | Authenticates Notion API requests. |
| `TFC_TOKEN` | Sensitive | Authenticates Terraform Cloud operations. |

## GitHub Workflow Mapping

| Workflow | Job | Terraform Inputs |
| --- | --- | --- |
| `.github/workflows/tfc-sync.yml` | `terraform` | Sets the working directory to `./infra` and exports the full variable suite to Terraform via `TF_VAR_` environment variables. |
| `.github/workflows/notion-sync.yml` | `test-and-sync` | Loads the `NOTION_TOKEN` secret for runtime API access while running tests before execution. |

## Repository Configuration
* Terraform variable declarations live in `infra/agent-variables.tf` with placeholder values in `infra/variables.tfvars`. 【F:infra/agent-variables.tf†L1-L46】【F:infra/variables.tfvars†L1-L12】
* GitHub Actions jobs now run Terraform from `infra/` with input prompts disabled to guarantee non-interactive CI executions. 【F:.github/workflows/tfc-sync.yml†L15-L39】
* Automation scripts reference the unified Notion token name and no longer require ad-hoc plan variables. 【F:scripts/notion_sync.py†L178-L210】

## Validation Log
The following commands were executed on 2025-04-28 to verify the configuration:

```
terraform fmt
terraform init -input=false -no-color
terraform validate -no-color
terraform plan -input=false -no-color -var-file=variables.tfvars
```

Outputs confirmed clean formatting, successful initialisation, valid configuration, and a no-op plan. 【7bc4a2†L1-L2】【9fe26b†L1-L14】【2042a2†L1-L3】【a96aff†L1-L5】

Terraform Cloud workspace verification link: _pending update after next automated run_.
